import os
import sys

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, size
from pyspark.sql.types import ArrayType, StringType

# 确保能导入当前目录的模块，并将 project_root 指向真正的项目根目录(上一级)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(current_dir)

from data_parser import DataParser
from spark_fpm_miner import SparkFPMMiner

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main():
    print("=" * 60)
    print("🚀 欢迎启动 HFPM-DDA (PySpark 大数据分布式重构版) 🚀")
    print("=" * 60)

    # 初始化 Spark Session
    spark = SparkSession.builder \
        .appName("HFPM-DDA-Spark-Pipeline") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .config("spark.pyspark.python", sys.executable) \
        .config("spark.pyspark.driver.python", sys.executable) \
        .config("spark.python.worker.timeout", 60) \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    parser = DataParser()
    miner = SparkFPMMiner(output_dir=os.path.join(project_root, "output"))

    print("\n--- [Phase 1: 异构数据解析 (Driver 端)] ---")
    drug_metadata = parser.parse_drugbank_metadata()
    disease_to_genes, ctd_disease_names = parser.parse_ctd_genes_diseases()

    # 向 Spark Workers 广播元数据字典，避免每个节点重复加载
    bc_drug_metadata = spark.sparkContext.broadcast(drug_metadata)

    print("\n--- [Phase 2: Spark 分布式加载全量临床数据 & 切分] ---")
    repodb_path = os.path.join(project_root, "data", "repoDB_full.csv")

    # 使用 Spark 读取 CSV
    df_repo = spark.read.csv(repodb_path, header=True, inferSchema=True)

    repodb_disease_names = {row['ind_id']: row['ind_name'] for row in
                            df_repo.select('ind_id', 'ind_name').dropDuplicates().collect()}

    df_approved = df_repo.filter(col("status") == "Approved")
    df_failed = df_repo.filter(col("status").isin("Terminated", "Withdrawn", "Suspended"))

    print(f"[Spark数据] 成功(Approved)记录: {df_approved.count()} 条")
    print(f"[Spark数据] 失败(Terminated/Withdrawn等)记录: {df_failed.count()} 条")

    # Spark 方式的数据集切分 (80% 训练 / 20% 测试)
    train_app, test_app = df_approved.randomSplit([0.8, 0.2], seed=42)
    train_fail, test_fail = df_failed.randomSplit([0.8, 0.2], seed=42)

    # 将 Spark 切分好的数据转为 Pandas 并保存为单文件 CSV
    out_dir = os.path.join(project_root, "output")
    os.makedirs(out_dir, exist_ok=True)

    print("\n--- [Phase 2.5: 正在将 Spark 切分好的数据集写入硬盘] ---")
    train_app.toPandas().to_csv(os.path.join(out_dir, "spark_train_approved.csv"), index=False, encoding='utf-8-sig')
    test_app.toPandas().to_csv(os.path.join(out_dir, "spark_test_approved.csv"), index=False, encoding='utf-8-sig')
    train_fail.toPandas().to_csv(os.path.join(out_dir, "spark_train_failed.csv"), index=False, encoding='utf-8-sig')
    test_fail.toPandas().to_csv(os.path.join(out_dir, "spark_test_failed.csv"), index=False, encoding='utf-8-sig')

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

    print("\n--- [Phase 3: 分布式事务映射构建 (UDF)] ---")

    # 定义 Spark UDF，使用广播变量在分布式节点上匹配事务
    def build_transaction(db_id, disease_id):
        metadata = bc_drug_metadata.value.get(db_id, {})
        features = metadata.get("features", [])
        if features:
            raw_transaction = features + [f"DISEASE_{disease_id}"]
            # 确保最终交给 Spark FPGrowth 的事务数组绝对唯一
            return list(dict.fromkeys(raw_transaction))
        return []

    transaction_udf = udf(build_transaction, ArrayType(StringType()))

    # 构建训练集事务集并过滤掉长度不足 2 的无效事务
    df_trans_app = train_app.withColumn("items", transaction_udf(col("drugbank_id"), col("ind_id")))
    df_trans_app = df_trans_app.filter(size(col("items")) >= 2).select("items")

    df_trans_fail = train_fail.withColumn("items", transaction_udf(col("drugbank_id"), col("ind_id")))
    df_trans_fail = df_trans_fail.filter(size(col("items")) >= 2).select("items")

    print(f"[构建器] 构建完成！有效训练集事务(Approved): {df_trans_app.count()} 条")

    print("\n--- [Phase 4: 训练集对比模式挖掘 (Spark MLlib)] ---")
    target_support = 0.003
    rules_df = miner.mine_rules(df_transactions=df_trans_app, min_support=target_support, min_confidence=0.15)

    if rules_df is not None:
        print("\n[分析器] 正在拉取失败集到本地计算对比指标 (Growth Rate)...")
        # 将失败的事务集收集回本地，以复用特异性计算逻辑
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

        print("\n🏆 Top 10 高特异性关联规则 (基于 Spark 分布式挖掘):")
        for idx, row in high_value_rules.head(10).iterrows():
            antecedents = ", ".join([format_item(x) for x in row['antecedents']])
            consequents = ", ".join([format_item(x) for x in row['consequents']])
            gr_display = "∞ (纯正向)" if row['growth_rate'] == float('inf') else f"{row['growth_rate']:.2f}"
            print(f"   前件: {antecedents} -> 后件: {consequents}")
            print(
                f"       (Support: {row['support']:.4f}, Confidence: {row['confidence']:.4f}, Lift: {row['lift']:.2f}, GrowthRate: {gr_display})")

        print("\n--- [Phase 5: 零样本药物重定位与双重验证] ---")

        # 将测试集对提取到本地，用于验证发现
        known_train_pairs = set(
            [(row['drugbank_id'], row['ind_id']) for row in train_app.select('drugbank_id', 'ind_id').collect()])
        test_pairs = set(
            [(row['drugbank_id'], row['ind_id']) for row in test_app.select('drugbank_id', 'ind_id').collect()])

        discovery_results = []
        for _, rule in high_value_rules.iterrows():
            antecedents_targets = set([x for x in rule['antecedents'] if str(x).startswith('TARGET_')])
            consequents_diseases = set([x for x in rule['consequents'] if str(x).startswith('DISEASE_')])

            if not antecedents_targets or not consequents_diseases: continue

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
            print(f"\n🚀 Spark 分析完成！共发现 {len(discovery_df)} 条重定位关联！")

            discovery_path = os.path.join(project_root, "output", "spark_new_drug_discoveries.csv")
            discovery_df.to_csv(discovery_path, index=False, encoding='utf-8-sig')
            print(f"✅ 包含 Spark 模型盲测验证标签的清单已保存至: {discovery_path}")
        else:
            print("未能发掘新组合。")

    spark.stop()
    print("\n✅ Spark 任务执行完毕，集群资源已释放！")


if __name__ == "__main__":
    main()
