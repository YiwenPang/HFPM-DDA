import os
import sys

import pandas as pd
from sklearn.model_selection import train_test_split

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_parser import DataParser
from transaction_builder import TransactionBuilder
from fpm_miner import FPMMiner


def main():
    print("=" * 60)
    print("🚀 欢迎启动 HFPM-DDA 关联规则深度挖掘与新药发现系统 🚀")
    print("=" * 60)

    parser = DataParser()
    miner = FPMMiner(output_dir=os.path.join(project_root, "output"))

    print("\n--- [Phase 1: 异构数据流式加载] ---")
    drug_metadata = parser.parse_drugbank_metadata()
    disease_to_genes, ctd_disease_names = parser.parse_ctd_genes_diseases()

    print("\n--- [Phase 2: 加载全量临床数据 & 构建对比集] ---")
    repodb_path = os.path.join(project_root, "data", "repoDB_full.csv")
    repodb_df = pd.read_csv(repodb_path)

    repodb_disease_names = dict(zip(repodb_df['ind_id'], repodb_df['ind_name']))

    df_approved = repodb_df[repodb_df['status'] == 'Approved']
    df_failed = repodb_df[repodb_df['status'].isin(['Terminated', 'Withdrawn', 'Suspended'])]
    print(f"[数据] 成功(Approved)记录: {len(df_approved)} 条")
    print(f"[数据] 失败(Terminated/Withdrawn等)记录: {len(df_failed)} 条")

    # ==========================================
    # 数据集切分 (80% 训练集 / 20% 测试集)
    # ==========================================
    print("\n--- [Phase 2.5: 数据集切分 (80% 训练集 / 20% 测试集)] ---")
    train_app, test_app = train_test_split(df_approved, test_size=0.2, random_state=42)
    train_fail, test_fail = train_test_split(df_failed, test_size=0.2, random_state=42)

    out_dir = os.path.join(project_root, "output")
    os.makedirs(out_dir, exist_ok=True)
    train_app.to_csv(os.path.join(out_dir, "train_approved.csv"), index=False, encoding='utf-8-sig')
    test_app.to_csv(os.path.join(out_dir, "test_approved.csv"), index=False, encoding='utf-8-sig')
    train_fail.to_csv(os.path.join(out_dir, "train_failed.csv"), index=False, encoding='utf-8-sig')
    test_fail.to_csv(os.path.join(out_dir, "test_failed.csv"), index=False, encoding='utf-8-sig')

    print(f"[划分] 训练集(Approved): {len(train_app)} 条已写入硬盘 | 测试集(Approved): {len(test_app)} 条已写入硬盘")

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

    print("\n--- [Phase 3: 对比事务映射构建] ---")
    builder = TransactionBuilder(drug_metadata)
    print("[构建 训练集 Approved 事务集]")
    trans_train_approved = builder.build_transactions(train_app)
    print("[构建 训练集 Failed 事务集]")
    trans_train_failed = builder.build_transactions(train_fail)
    trans_train_failed_sets = [set(t) for t in trans_train_failed]

    print("\n--- [Phase 4: 训练集对比模式挖掘] ---")
    target_support = 0.003

    rules_df = miner.mine_rules(
        transactions=trans_train_approved,
        min_support=target_support,
        min_confidence=0.15
    )

    if rules_df is not None:
        print("\n[挖掘机] 正在基于训练集计算对比指标 (Growth Rate)...")
        growth_rates = []
        support_failed_list = []
        failed_count = len(trans_train_failed_sets)

        for _, row in rules_df.iterrows():
            rule_items = row['antecedents'] | row['consequents']
            match_count = sum(1 for t in trans_train_failed_sets if rule_items.issubset(t))
            supp_failed = match_count / failed_count if failed_count > 0 else 0
            support_failed_list.append(supp_failed)

            if supp_failed == 0:
                gr = float('inf')
            else:
                gr = row['support'] / supp_failed
            growth_rates.append(gr)

        rules_df['support_failed'] = support_failed_list
        rules_df['growth_rate'] = growth_rates

        high_value_rules = rules_df[rules_df['growth_rate'] > 3.0].sort_values(by=['growth_rate', 'lift'],
                                                                               ascending=[False, False])

        print("\n🏆 Top 10 高特异性关联规则 (源自训练集):")
        for idx, row in high_value_rules.head(10).iterrows():
            antecedents = ", ".join([format_item(x) for x in row['antecedents']])
            consequents = ", ".join([format_item(x) for x in row['consequents']])
            gr_display = "∞ (纯正向)" if row['growth_rate'] == float('inf') else f"{row['growth_rate']:.2f}"
            print(f"   前件: {antecedents} -> 后件: {consequents}")
            print(
                f"       (Support: {row['support']:.4f}, Confidence: {row['confidence']:.4f}, Lift: {row['lift']:.2f}, GrowthRate: {gr_display})")

        print("\n--- [Phase 5: 零样本药物重定位与双重验证 (Knowledge Discovery)] ---")

        known_train_pairs = set(zip(train_app['drugbank_id'], train_app['ind_id']))
        test_pairs = set(zip(test_app['drugbank_id'], test_app['ind_id']))

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
            disease_genes_raw = disease_to_genes.get(ctd_query_id, [])

            if not disease_genes_raw:
                disease_genes_raw = disease_to_genes.get(str(disease_name).lower(), [])

            disease_gene_bases = {str(g).replace("GENE_", "").upper() for g in disease_genes_raw}

            for db_id, info in drug_metadata.items():
                drug_features = set(info.get("features", []))
                drug_genes = info.get("genes", [])

                if antecedents_targets.issubset(drug_features):
                    # 只要不在训练集里的，都是模型的“重定位预测输出”
                    if (db_id, target_disease_id) not in known_train_pairs:
                        # 核心校验：该推论是否落在了未知的 20% 测试集里
                        is_hit = (db_id, target_disease_id) in test_pairs
                        status = "✅ 验证集完美命中" if is_hit else "🌟 零样本全新发现"

                        bridge_genes = drug_genes.intersection(disease_gene_bases)
                        bridge_display = ", ".join(bridge_genes) if bridge_genes else "间接机制"

                        discovery_results.append({
                            "DrugBank_ID": db_id,
                            "Drug_Name": info.get("name", db_id),
                            "Predicted_Disease_ID": target_disease_id,
                            "Predicted_Disease_Name": disease_name,
                            "Matched_Targets": ", ".join(antecedents_targets),
                            "Bridging_Genes": bridge_display,
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

            print(f"🚀 系统分析完成！共发现 {len(discovery_df)} 条潜在药物重定位关联！")
            print(f"   📊 统计验证：成功命中 20% 盲测集真实临床数据: {hits_count} 条")
            print(f"   🔭 科学探索：挖掘出超出已知数据库的全新潜在靶向组合: {novel_count} 条")

            # ==========================================
            # 输出 1：按照置信度排序 (保留原样)
            # ==========================================
            print("\n🌟 Top 15 新药重定位候选推荐 (按置信度排序 - 反应治愈概率):")
            top_15_df = discovery_df.head(15)
            for idx, row in top_15_df.iterrows():
                gr_str = "∞" if row['Rule_Growth_Rate'] == float('inf') else f"{row['Rule_Growth_Rate']:.2f}"
                print(
                    f"   💊 药物: {row['Drug_Name']} -> 🎯 预测主治: {row['Predicted_Disease_Name']}  [{row['Validation_Status']}]")
                print(
                    f"      (靶向机制: {row['Matched_Targets']}\n       关联基因: {row['Bridging_Genes']} | 置信度: {row['Rule_Confidence']:.4f} | 特异性: {gr_str})")

            # ==========================================
            # 输出 2：新增按照增长率（特异性）排序
            # ==========================================
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

            # ==========================================
            # 输出 3：长尾探索 (消除头部霸屏)
            # ==========================================
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

            # 导出 CSV 供后续分析
            discovery_path = os.path.join(project_root, "output", "new_drug_discoveries.csv")
            discovery_df.to_csv(discovery_path, index=False, encoding='utf-8-sig')
            print(f"\n✅ 包含模型盲测验证标签的重定位清单已保存至: {discovery_path}")
        else:
            print("目前高特异性规则暂未在现有数据库中匹配到全新未知的组合。")

    else:
        print("[警告] 训练集未挖掘出任何规则，请检查参数或调高 min_support 后重试。")

    print("\n✅ 全流程执行完毕！")


if __name__ == "__main__":
    main()
