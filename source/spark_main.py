import os
import sys

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, size, explode, count as spark_count
from pyspark.sql.types import ArrayType, StringType
from sklearn.model_selection import train_test_split

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(current_dir)

from data_parser import DataParser
from spark_fpm_miner import SparkFPMMiner, RuleRefiner

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main():
    print("=" * 60)
    print("🚀 欢迎启动 HFPM-DDA (PySpark 大数据分布式重构版) 🚀")
    print("=" * 60)

    # 初始化 Spark Session
    spark = SparkSession.builder \
        .appName("HFPM-DDA-Spark-Pipeline") \
        .master("local[2]") \
        .config("spark.driver.memory", "16g") \
        .config("spark.executor.memory", "16g") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "false") \
        .config("spark.python.worker.reuse", "false") \
        .config("spark.python.worker.timeout", 300) \
        .config("spark.pyspark.python", sys.executable) \
        .config("spark.pyspark.driver.python", sys.executable) \
        .config("spark.python.worker.faulthandler.enabled", "true") \
        .config("spark.sql.execution.pyspark.udf.faulthandler.enabled", "true") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    parser = DataParser()

    out_dir = os.path.join(project_root, "output")
    os.makedirs(out_dir, exist_ok=True)
    miner = SparkFPMMiner(output_dir=out_dir)

    print("\n--- [Phase 1: 异构数据解析 (Driver 端)] ---")
    drug_metadata = parser.parse_drugbank_metadata()
    disease_to_genes, ctd_disease_names = parser.parse_ctd_genes_diseases()

    # 向 Spark Workers 广播元数据字典
    bc_drug_metadata = spark.sparkContext.broadcast(drug_metadata)

    print("\n--- [Phase 2: 加载全量临床数据 & 严格对齐切分 (Driver 端)] ---")
    repodb_path = os.path.join(project_root, "data", "repoDB_full.csv")

    repodb_df = pd.read_csv(repodb_path)
    repodb_disease_names = dict(zip(repodb_df['ind_id'], repodb_df['ind_name']))

    df_approved_pd = repodb_df[repodb_df['status'] == 'Approved']
    df_failed_pd = repodb_df[repodb_df['status'].isin(['Terminated', 'Withdrawn', 'Suspended'])]

    print(f"[数据] 成功(Approved)记录: {len(df_approved_pd)} 条")
    print(f"[数据] 失败(Terminated/Withdrawn等)记录: {len(df_failed_pd)} 条")

    # 严格的 80/20 随机种子切分
    train_app_pd, test_app_pd = train_test_split(df_approved_pd, test_size=0.2, random_state=42)
    train_fail_pd, test_fail_pd = train_test_split(df_failed_pd, test_size=0.2, random_state=42)

    print("\n--- [Phase 2.5: 本地写盘 & 转换为 Spark DataFrame] ---")
    train_app_pd.to_csv(os.path.join(out_dir, "spark_train_approved.csv"), index=False, encoding='utf-8-sig')
    test_app_pd.to_csv(os.path.join(out_dir, "spark_test_approved.csv"), index=False, encoding='utf-8-sig')
    train_fail_pd.to_csv(os.path.join(out_dir, "spark_train_failed.csv"), index=False, encoding='utf-8-sig')
    test_fail_pd.to_csv(os.path.join(out_dir, "spark_test_failed.csv"), index=False, encoding='utf-8-sig')

    train_app = spark.createDataFrame(train_app_pd)
    test_app = spark.createDataFrame(test_app_pd)
    train_fail = spark.createDataFrame(train_fail_pd)
    test_fail = spark.createDataFrame(test_fail_pd)  # ？？？

    print(
        f"[Spark划分] 训练集(Approved): {train_app.count()} 条已写入硬盘 | 测试集(Approved): {test_app.count()} 条已写入硬盘")

    def get_disease_name(dis_id):
        clean_id = str(dis_id).replace("DISEASE_", "")
        if clean_id in repodb_disease_names:
            return repodb_disease_names[clean_id]
        mesh_id = clean_id if clean_id.startswith("MESH:") else f"MESH:{clean_id}"
        return ctd_disease_names.get(mesh_id, clean_id)

    def format_item(item):
        item_str = str(item)
        if item_str.startswith("DISEASE_"):
            return f"【{get_disease_name(item_str)}】"
        elif item_str.startswith("TARGET_") or item_str.startswith("GENE_"):
            return f"[{item_str}]"
        return item_str

    print("\n--- [Phase 3: 分布式事务映射构建与严格剪枝 (UDF)] ---")

    def build_transaction(db_id, disease_id):
        metadata = bc_drug_metadata.value.get(db_id, {})
        features = metadata.get("features", [])
        if features:
            raw_transaction = features + [f"DISEASE_{disease_id}"]
            unique_transaction = list(dict.fromkeys(raw_transaction))
            has_disease = any(str(item).startswith("DISEASE_") for item in unique_transaction)
            if has_disease and len(unique_transaction) >= 2:
                return unique_transaction
        return []

    transaction_udf = udf(build_transaction, ArrayType(StringType()))

    df_trans_app = train_app.withColumn("items", transaction_udf(col("drugbank_id"), col("ind_id")))
    df_trans_app = df_trans_app.filter(size(col("items")) > 0).select("items")
    df_trans_app = df_trans_app.cache()

    df_trans_fail = train_fail.withColumn("items", transaction_udf(col("drugbank_id"), col("ind_id")))
    df_trans_fail = df_trans_fail.filter(size(col("items")) > 0).select("items")
    df_trans_fail = df_trans_fail.cache()

    print(f"[构建器] 构建完成！剪枝后有效训练集事务(Approved): {df_trans_app.count()} 条")

    print("\n--- [Phase 4: 训练集对比模式挖掘 (Spark MLlib)] ---")
    target_support = 0.003

    # 前置项集频率剪枝
    print("\n[剪枝] 正在执行前置项集频率剪枝...")
    total_trans = df_trans_app.count()
    min_support_count = target_support * total_trans

    item_freq = (df_trans_app
                 .select(explode("items").alias("item"))
                 .groupBy("item")
                 .agg(spark_count("*").alias("cnt"))
                 .filter(col("cnt") >= min_support_count))

    freq_items = [row.item for row in item_freq.select("item").collect()]
    original_unique = df_trans_app.select(explode("items").alias("item")).distinct().count()
    print(f"[剪枝] 有效词表大小从 {original_unique} 缩减至 {len(freq_items)}")
    bc_freq_items = spark.sparkContext.broadcast(set(freq_items))

    def prune_transaction(items):
        filtered = [it for it in items if it in bc_freq_items.value]
        # 必须仍包含至少一个疾病标签，且长度 >= 2
        has_disease = any(it.startswith("DISEASE_") for it in filtered)
        return filtered if (has_disease and len(filtered) >= 2) else []

    prune_udf = udf(prune_transaction, ArrayType(StringType()))

    df_trans_app_pruned = (df_trans_app
                           .withColumn("items", prune_udf(col("items")))
                           .filter(size(col("items")) >= 2)
                           .select("items")
                           .cache())

    pruned_count = df_trans_app_pruned.count()
    print(f"[剪枝] 有效事务数从 {total_trans} 缩减至 {pruned_count}")

    # 使用剪枝后的数据挖掘规则
    rules_df = miner.mine_rules(df_transactions=df_trans_app_pruned, min_support=target_support, min_confidence=0.15)

    if rules_df is not None and not rules_df.empty:
        print("\n[分析器] 正在拉取失败集到本地计算对比指标 (Growth Rate)...")
        trans_train_failed_sets = [set(row.items) for row in df_trans_fail.collect()]
        failed_count = len(trans_train_failed_sets)

        growth_rates = []
        support_failed_list = []

        for _, row in rules_df.iterrows():
            rule_items = row['antecedents'] | row['consequents']
            match_count = sum(1 for t in trans_train_failed_sets if rule_items.issubset(t))
            supp_failed = match_count / failed_count if failed_count > 0 else 0
            support_failed_list.append(supp_failed)

            gr = float('inf') if supp_failed == 0 else row['support'] / supp_failed
            growth_rates.append(gr)

        rules_df['support_failed'] = support_failed_list
        rules_df['growth_rate'] = growth_rates

        high_value_rules = rules_df[rules_df['growth_rate'] > 3.0].sort_values(by=['growth_rate', 'lift'],
                                                                               ascending=[False, False])

        print("\n--- [Phase 4.5: Spark分布式结果精炼与去冗余] ---")
        pre_count = len(high_value_rules)
        high_value_rules = RuleRefiner.remove_redundant_rules(high_value_rules)
        print(f"🧹 [去冗余] 成功抹除 {pre_count - len(high_value_rules)} 条同质化超集规则。")

        rep_rules = RuleRefiner.extract_representative_rules(high_value_rules)
        print("\n🥇 Spark挖掘各疾病高分代表机制:")
        for idx, row in rep_rules.head(10).iterrows():
            antecedents = ", ".join([format_item(x) for x in row['antecedents']])
            cons_item = list(row['consequents'])[0]
            dis_name = get_disease_name(cons_item)
            gr_display = "∞" if row['growth_rate'] == float('inf') else f"{row['growth_rate']:.2f}"
            print(f"   🎯 疾病: 【{dis_name}】")
            print(f"       => 核心靶向机制: {antecedents}")
            print(
                f"       => [Score: {row['rep_score']:.1f} | Conf: {row['confidence']:.4f} | Supp: {row['support']:.4f} | GR: {gr_display}]")

        print("\n🏆 Top 10 高特异性关联规则 (基于 Spark 分布式挖掘, 多样性筛选):")
        diverse_top_rules = RuleRefiner.get_diverse_top_rules(high_value_rules, top_n=10, max_per_disease=2)
        for idx, row in diverse_top_rules.iterrows():
            antecedents = ", ".join([format_item(x) for x in row['antecedents']])
            consequents = ", ".join([format_item(x) for x in row['consequents']])
            gr_display = "∞ (纯正向)" if row['growth_rate'] == float('inf') else f"{row['growth_rate']:.2f}"
            print(f"   前件: {antecedents} -> 后件: {consequents}")
            print(
                f"       (Support: {row['support']:.4f}, Confidence: {row['confidence']:.4f}, GrowthRate: {gr_display})")

        print("\n--- [Phase 5: 零样本药物重定位与双重验证] ---")

        known_train_pairs = set(
            [(row['drugbank_id'], row['ind_id']) for row in train_app.select('drugbank_id', 'ind_id').collect()])
        test_pairs = set(
            [(row['drugbank_id'], row['ind_id']) for row in test_app.select('drugbank_id', 'ind_id').collect()])

        discovery_results = []
        for _, rule in high_value_rules.iterrows():
            antecedents_targets = set([x for x in rule['antecedents'] if str(x).startswith('TARGET_')])
            consequents_diseases = set([x for x in rule['consequents'] if str(x).startswith('DISEASE_')])

            if not antecedents_targets or not consequents_diseases:
                continue

            target_disease_id = list(consequents_diseases)[0].replace("DISEASE_", "")
            disease_name = get_disease_name(target_disease_id)

            ctd_query_id = target_disease_id if str(target_disease_id).startswith(
                "MESH:") else f"MESH:{target_disease_id}"
            disease_genes_raw = disease_to_genes.get(ctd_query_id, disease_to_genes.get(str(disease_name).lower(), []))
            disease_gene_bases = {str(g).replace("GENE_", "").upper() for g in disease_genes_raw}

            for db_id, info in drug_metadata.items():
                drug_features = set(info.get("features", []))
                drug_genes = info.get("genes", [])

                if antecedents_targets.issubset(drug_features):
                    if (db_id, target_disease_id) not in known_train_pairs:
                        is_hit = (db_id, target_disease_id) in test_pairs
                        status = "✅ Spark验证集完美命中" if is_hit else "🌟 零样本全新发现"
                        bridge_genes = drug_genes.intersection(disease_gene_bases)

                        discovery_results.append({
                            "DrugBank_ID": db_id,
                            "Drug_Name": info.get("name", db_id),
                            "Predicted_Disease_ID": target_disease_id,
                            "Predicted_Disease_Name": disease_name,
                            "Matched_Targets": ", ".join(antecedents_targets),
                            "Bridging_Genes": ", ".join(bridge_genes) if bridge_genes else "间接机制",
                            "Rule_Confidence": rule['confidence'],
                            "Rule_Growth_Rate": rule['growth_rate'],
                            "Validation_Status": status
                        })

        discovery_df = pd.DataFrame(discovery_results)
        if not discovery_df.empty:
            discovery_df = discovery_df.drop_duplicates(subset=['DrugBank_ID', 'Predicted_Disease_ID']).sort_values(
                by='Rule_Confidence', ascending=False)

            hits_count = len(discovery_df[discovery_df['Validation_Status'].str.contains("命中")])
            novel_count = len(discovery_df) - hits_count

            print(f"\n🚀 Spark 分析完成！共发现 {len(discovery_df)} 条潜在药物重定位关联！")
            print(f"   📊 统计验证：成功命中 20% 盲测集真实临床数据: {hits_count} 条")
            print(f"   🔭 科学探索：挖掘出超出已知数据库的全新潜在靶向组合: {novel_count} 条")

            print("\n🌟 Top 15 新药重定位候选推荐 (按置信度排序 - 反应治愈概率):")
            top_15_df = discovery_df.head(15)
            for idx, row in top_15_df.iterrows():
                gr_str = "∞" if row['Rule_Growth_Rate'] == float('inf') else f"{row['Rule_Growth_Rate']:.2f}"
                print(
                    f"   💊 药物: {row['Drug_Name']} -> 🎯 预测主治: {row['Predicted_Disease_Name']}  [{row['Validation_Status']}]")
                print(
                    f"      (靶向机制: {row['Matched_Targets']}\n       关联基因: {row['Bridging_Genes']} | 置信度: {row['Rule_Confidence']:.4f} | 特异性: {gr_str})")

            print("\n🔥 Top 15 新药重定位候选推荐 (按特异性/增长率排序 - 反应靶向独特性):")
            discovery_df_by_growth = discovery_df.sort_values(by=['Rule_Growth_Rate', 'Rule_Confidence'],
                                                              ascending=[False, False])
            top_15_growth_df = discovery_df_by_growth.head(15)
            for idx, row in top_15_growth_df.iterrows():
                gr_str = "∞" if row['Rule_Growth_Rate'] == float('inf') else f"{row['Rule_Growth_Rate']:.2f}"
                print(
                    f"   💊 药物: {row['Drug_Name']} -> 🎯 预测主治: {row['Predicted_Disease_Name']}  [{row['Validation_Status']}]")
                print(
                    f"      (靶向机制: {row['Matched_Targets']}\n       关联基因: {row['Bridging_Genes']} | 置信度: {row['Rule_Confidence']:.4f} | 特异性: {gr_str})")

            print("\n🌈 更多长尾/多样的重定位候选:")
            displayed_diseases = set(top_15_df['Predicted_Disease_ID']).union(
                set(top_15_growth_df['Predicted_Disease_ID']))
            seen_diverse_diseases = set()
            diverse_count = 0

            for idx, row in discovery_df.iterrows():
                dis_id = row['Predicted_Disease_ID']
                if dis_id not in displayed_diseases and dis_id not in seen_diverse_diseases:
                    gr_str = "∞" if row['Rule_Growth_Rate'] == float('inf') else f"{row['Rule_Growth_Rate']:.2f}"
                    print(
                        f"   💊 药物: {row['Drug_Name']} -> 🎯 预测主治: {row['Predicted_Disease_Name']}  [{row['Validation_Status']}]")
                    print(
                        f"      (靶向机制: {row['Matched_Targets']}\n       关联基因: {row['Bridging_Genes']} | 置信度: {row['Rule_Confidence']:.4f} | 特异性: {gr_str})")

                    seen_diverse_diseases.add(dis_id)
                    diverse_count += 1
                    if diverse_count >= 15:
                        break

            discovery_path = os.path.join(out_dir, "spark_new_drug_discoveries.csv")
            discovery_df.to_csv(discovery_path, index=False, encoding='utf-8-sig')
            print(f"✅ 包含 Spark 模型盲测验证标签的清单已保存至: {discovery_path}")

        else:
            print("未能发掘新组合。")
    else:
        print("[警告] 训练集未挖掘出任何规则，请检查参数或调高 min_support 后重试。")

    spark.stop()
    print("\n✅ Spark 任务执行完毕，集群资源已释放！")


if __name__ == "__main__":
    main()
