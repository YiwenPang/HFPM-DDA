import os
import sys

import pandas as pd

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_parser import DataParser
from transaction_builder import TransactionBuilder
from fpm_miner import FPMMiner


def main():
    print("=" * 50)
    print("🚀 欢迎启动 HFPM-DDA 关联规则深度挖掘与新药发现系统 🚀")
    print("=" * 50)

    parser = DataParser()
    miner = FPMMiner()

    print("\n--- [Phase 1: 异构数据流式加载] ---")
    drug_metadata = parser.parse_drugbank_metadata()
    disease_to_genes, ctd_disease_names = parser.parse_ctd_genes_diseases()

    print("\n--- [Phase 2: 加载全量临床数据 & 构建对比集] ---")
    repodb_path = os.path.join(project_root, "data", "repoDB_full.csv")
    repodb_df = pd.read_csv(repodb_path)

    repodb_drug_names = dict(zip(repodb_df['drugbank_id'], repodb_df['drug_name']))
    repodb_disease_names = dict(zip(repodb_df['ind_id'], repodb_df['ind_name']))

    df_approved = repodb_df[repodb_df['status'] == 'Approved']
    df_failed = repodb_df[repodb_df['status'].isin(['Terminated', 'Withdrawn', 'Suspended'])]
    print(f"[数据] 成功(Approved)记录: {len(df_approved)} 条")
    print(f"[数据] 失败(Terminated/Withdrawn等)记录: {len(df_failed)} 条")

    def get_drug_name(db_id):
        clean_id = str(db_id).replace("DRUG_", "")
        if clean_id in drug_metadata:
            return drug_metadata[clean_id].get("name", clean_id)
        return repodb_drug_names.get(clean_id, clean_id)

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
        elif item_str.startswith("DRUG_"):
            return f"【{get_drug_name(item_str)}】"
        return item_str

    print("\n--- [Phase 3: 对比事务映射构建] ---")
    builder = TransactionBuilder(drug_metadata)
    print("[构建 Approved 事务集]")
    trans_approved = builder.build_transactions(df_approved)
    print("[构建 Failed 事务集]")
    trans_failed = builder.build_transactions(df_failed)

    trans_failed_sets = [set(t) for t in trans_failed]

    print("\n--- [Phase 4: 对比模式挖掘] ---")

    # min_support=0.0014: 完美平衡点。既能挖出高阶多靶点组合，又把项集总数卡在物理内存安全线内。
    # min_confidence=0.25: 允许部分具有潜力的弱广义关联进入筛选池。
    rules_df = miner.mine_rules(
        transactions=trans_approved,
        min_support=0.0016,
        min_confidence=0.25
    )

    if rules_df is not None:
        print("\n[挖掘机] 正在计算对比指标 (Growth Rate)...")
        growth_rates = []
        support_failed_list = []
        failed_count = len(trans_failed_sets)

        for _, row in rules_df.iterrows():
            rule_items = row['antecedents'] | row['consequents']
            match_count = sum(1 for t in trans_failed_sets if rule_items.issubset(t))
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

        print("\n🏆 Top 10 高特异性关联规则 (Emerging Patterns):")
        for idx, row in high_value_rules.head(10).iterrows():
            antecedents = ", ".join([format_item(x) for x in row['antecedents']])
            consequents = ", ".join([format_item(x) for x in row['consequents']])
            gr_display = "∞ (纯正向)" if row['growth_rate'] == float('inf') else f"{row['growth_rate']:.2f}"
            print(f"   前件: {antecedents} -> 后件: {consequents}")
            print(
                f"       (Support: {row['support']:.4f}, Confidence: {row['confidence']:.4f}, Lift: {row['lift']:.2f}, GrowthRate: {gr_display})")

        print("\n--- [Phase 5: 零样本药物重定位 (Knowledge Discovery)] ---")

        known_pairs = set(zip(df_approved['drugbank_id'], df_approved['ind_id']))
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
                    if (db_id, target_disease_id) not in known_pairs:
                        bridge_genes = drug_genes.intersection(disease_gene_bases)
                        bridge_display = ", ".join(bridge_genes) if bridge_genes else "无直接重合(间接机制)"

                        discovery_results.append({
                            "DrugBank_ID": db_id,
                            "Drug_Name": info.get("name", db_id),
                            "Predicted_Disease_ID": target_disease_id,
                            "Predicted_Disease_Name": disease_name,
                            "Matched_Targets": ", ".join(antecedents_targets),
                            "Bridging_Genes": bridge_display,
                            "Rule_Confidence": rule['confidence'],
                            "Rule_Growth_Rate": rule['growth_rate']
                        })

        discovery_df = pd.DataFrame(discovery_results)

        if not discovery_df.empty:
            discovery_df = discovery_df.drop_duplicates(subset=['DrugBank_ID', 'Predicted_Disease_ID']).sort_values(
                by='Rule_Confidence', ascending=False)

            print(f"🚀 系统成功挖掘出 {len(discovery_df)} 条全新潜在重定位关联！")

            print("🌟 Top 15 新药重定位候选推荐 (按置信度排序):")
            top_15_df = discovery_df.head(15)
            for idx, row in top_15_df.iterrows():
                gr_str = "∞" if row['Rule_Growth_Rate'] == float('inf') else f"{row['Rule_Growth_Rate']:.2f}"
                print(f"   💊 药物: {row['Drug_Name']} -> 🎯 预测主治: {row['Predicted_Disease_Name']}")
                print(
                    f"      (靶向机制: {row['Matched_Targets']}\n       关联基因: {row['Bridging_Genes']} | 置信度: {row['Rule_Confidence']:.4f} | 特异性: {gr_str})")

            print("\n🌈 更多长尾/多样的重定位候选 (消除头部霸屏，展示不同病种):")
            displayed_diseases = set(top_15_df['Predicted_Disease_ID'])
            seen_diverse_diseases = set()
            diverse_count = 0

            for idx, row in discovery_df.iloc[15:].iterrows():
                dis_id = row['Predicted_Disease_ID']

                if dis_id not in displayed_diseases and dis_id not in seen_diverse_diseases:
                    gr_str = "∞" if row['Rule_Growth_Rate'] == float('inf') else f"{row['Rule_Growth_Rate']:.2f}"
                    print(f"   💊 药物: {row['Drug_Name']} -> 🎯 预测主治: {row['Predicted_Disease_Name']}")
                    print(
                        f"      (靶向机制: {row['Matched_Targets']}\n       关联基因: {row['Bridging_Genes']} | 置信度: {row['Rule_Confidence']:.4f} | 特异性: {gr_str})")

                    seen_diverse_diseases.add(dis_id)
                    diverse_count += 1
                    if diverse_count >= 15:
                        break

            # 添加 encoding='utf-8-sig'，彻底解决 Excel 打开新药发现清单乱码的问题
            discovery_path = os.path.join(project_root, "output", "new_drug_discoveries.csv")
            discovery_df.to_csv(discovery_path, index=False, encoding='utf-8-sig')
            print(f"\n✅ 完整的新药重定位候选清单已保存至: {discovery_path}")
        else:
            print("目前高特异性规则暂未在现有数据库中匹配到全新未知的组合。")

    else:
        print("[警告] 未挖掘出任何规则，请尝试调低 FP-Growth 的 min_support。")

    print("\n✅ 全流程执行完毕！")


if __name__ == "__main__":
    main()
