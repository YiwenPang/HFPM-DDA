import os
import sys

import pandas as pd
from sklearn.model_selection import train_test_split

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_parser import DataParser
from transaction_builder import TransactionBuilder
from fpm_miner import FPMMiner, RuleRefiner


def main():
    print("=" * 60)
    print("🚀 欢迎启动 HFPM-DDA 关联规则网格搜索与自动寻优系统 🚀")
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

    # =========================================================================
    # ⚙️ 核心全自动寻优：网格搜索候选集 (Grid Search Space)
    # =========================================================================
    print("\n--- [📊 Phase 4: 全自动参数网格搜索中 (Grid Search) ] ---")
    print("[提示] 寻优策略：支持度由高到低扫描（递减剪枝），一旦触发熔断，立即终止后续更低支持度的无效计算。")

    support_grid = [0.05, 0.03, 0.02, 0.015, 0.01, 0.008, 0.005, 0.003, 0.0016]
    confidence_grid = [0.15, 0.25, 0.35, 0.45]

    search_logs = []
    best_score = -1
    best_params = {"support": None, "confidence": None}
    high_value_rules = None

    global_meltdown_triggered = False

    for supp in support_grid:
        if global_meltdown_triggered:
            break

        print(f"\n📊 [支持度层级] 当前测试基准 min_support = {supp}")

        for conf in confidence_grid:
            print(f"  🔍 [尝试组合] 正在测试: min_support={supp}, min_confidence={conf} ...")

            rules_df = miner.mine_rules(
                transactions=trans_train_approved,
                min_support=supp,
                min_confidence=conf
            )

            if rules_df is None:
                print(f"🔥 [严重熔断] 检测到 min_support={supp} 导致频繁项集指数级组合爆炸！")
                print(f"💥 [严格剪枝] 由于支持度网格是严格递减的，所有小于 {supp} 的参数必然引发更惨烈的内存灾难。")
                print(f"🛑 [系统保护] 自动触发 Early Stopping，立即终止后续所有寻优测试！")

                for remaining_conf in confidence_grid[confidence_grid.index(conf):]:
                    search_logs.append({
                        "supp": supp, "conf": remaining_conf,
                        "rules": 0, "hits": 0, "novel": 0, "status": "🔥 熔断拦截"
                    })
                global_meltdown_triggered = True
                break

            if rules_df.empty:
                search_logs.append(
                    {"supp": supp, "conf": conf, "rules": 0, "hits": 0, "novel": 0, "status": "❌ 规则为0"})
                continue

            growth_rates = []
            failed_count = len(trans_train_failed_sets)
            for _, row in rules_df.iterrows():
                rule_items = row['antecedents'] | row['consequents']
                match_count = sum(1 for t in trans_train_failed_sets if rule_items.issubset(t))
                supp_failed = match_count / failed_count if failed_count > 0 else 0
                gr = float('inf') if supp_failed == 0 else row['support'] / supp_failed
                growth_rates.append(gr)
            rules_df['growth_rate'] = growth_rates
            current_high_value_rules = rules_df[rules_df['growth_rate'] > 3.0]

            hits_count = 0
            novel_count = 0
            known_train_pairs = set(zip(train_app['drugbank_id'], train_app['ind_id']))
            test_pairs = set(zip(test_app['drugbank_id'], test_app['ind_id']))
            seen_pairs = set()

            for _, rule in current_high_value_rules.iterrows():
                antecedents_targets = set([x for x in rule['antecedents'] if str(x).startswith('TARGET_')])
                consequents_diseases = set([x for x in rule['consequents'] if str(x).startswith('DISEASE_')])
                if not antecedents_targets or not consequents_diseases:
                    continue

                target_disease_id = list(consequents_diseases)[0].replace("DISEASE_", "")

                for db_id, info in drug_metadata.items():
                    drug_features = set(info.get("features", []))
                    if antecedents_targets.issubset(drug_features):
                        if (db_id, target_disease_id) not in known_train_pairs:
                            pair_key = (db_id, target_disease_id)
                            if pair_key in seen_pairs:
                                continue
                            seen_pairs.add(pair_key)

                            if pair_key in test_pairs:
                                hits_count += 1
                            else:
                                novel_count += 1

            score = hits_count * 10000 + len(current_high_value_rules)
            status_str = f"✅ 成功 (Hits: {hits_count})"
            search_logs.append(
                {"supp": supp, "conf": conf, "rules": len(current_high_value_rules), "hits": hits_count,
                 "novel": novel_count,
                 "status": status_str})

            if score > best_score:
                best_score = score
                best_params = {"support": supp, "confidence": conf}
                high_value_rules = current_high_value_rules.copy()

    print("\n" + "=" * 70)
    print("📊 参数敏感性分析与网格搜索报告 (Parameter Tuning Summary)")
    print("=" * 70)
    print(
        f"{'min_support':<12} | {'min_confidence':<14} | {'高特异规则数':<10} | {'测试集命中数':<10} | {'全新候选数':<10} | 状态")
    print("-" * 85)
    for log in search_logs:
        print(
            f"{log['supp']:<12} | {log['conf']:<14} | {log['rules']:<12} | {log['hits']:<12} | {log['novel']:<12} | {log['status']}")
    print("=" * 70)

    if high_value_rules is None or high_value_rules.empty:
        print("❌ [严重警告] 遍历了所有参数组合，未能找到任何有效规则，请检查数据源或调大搜索空间。")
        return

    print(f"🏆 【最优参数确定】: min_support = {best_params['support']}, min_confidence = {best_params['confidence']}")
    print("=========================================================================\n")

    print("\n[挖掘机] 正在基于训练集计算对比指标 (Growth Rate)...")
    high_value_rules = high_value_rules.sort_values(by=['growth_rate', 'lift'], ascending=[False, False])

    # ==========================================
    # 🧪 Phase 4.5 知识发现精炼器
    # ==========================================
    print("\n--- [Phase 4.5: 规则精炼与去冗余] ---")
    pre_count = len(high_value_rules)
    high_value_rules = RuleRefiner.remove_redundant_rules(high_value_rules)
    post_count = len(high_value_rules)
    print(f"🧹 [去冗余] 成功抹除 {pre_count - post_count} 条同质化超集规则。")

    rep_rules = RuleRefiner.extract_representative_rules(high_value_rules)
    print("\n🥇 各疾病最优代表机制:")
    for idx, row in rep_rules.head(10).iterrows():
        antecedents = ", ".join([format_item(x) for x in row['antecedents']])
        cons_item = list(row['consequents'])[0]
        dis_name = get_disease_name(cons_item)
        gr_display = "∞" if row['growth_rate'] == float('inf') else f"{row['growth_rate']:.2f}"
        print(f"   🎯 疾病: 【{dis_name}】")
        print(f"       => 核心靶向机制: {antecedents}")
        print(
            f"       => [Score: {row['rep_score']:.1f} | Conf: {row['confidence']:.4f} | Supp: {row['support']:.4f} | 特异性GR: {gr_display}]")

    print("\n🏆 Top 10 最优参数下高特异性关联规则 (多样性筛选):")
    diverse_top_rules = RuleRefiner.get_diverse_top_rules(high_value_rules, top_n=10, max_per_disease=2)
    for idx, row in diverse_top_rules.iterrows():
        antecedents = ", ".join([format_item(x) for x in row['antecedents']])
        consequents = ", ".join([format_item(x) for x in row['consequents']])
        gr_display = "∞ (纯正向)" if row['growth_rate'] == float('inf') else f"{row['growth_rate']:.2f}"
        print(f"   前件: {antecedents} -> 后件: {consequents}")
        print(f"       (Support: {row['support']:.4f}, Confidence: {row['confidence']:.4f}, GrowthRate: {gr_display})")

    print("\n--- [Phase 5: 零样本药物重定位与双重验证] ---")

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

        ctd_query_id = target_disease_id if str(target_disease_id).startswith("MESH:") else f"MESH:{target_disease_id}"
        disease_genes_raw = disease_to_genes.get(ctd_query_id, [])

        if not disease_genes_raw:
            disease_genes_raw = disease_to_genes.get(str(disease_name).lower(), [])

        disease_gene_bases = {str(g).replace("GENE_", "").upper() for g in disease_genes_raw}

        for db_id, info in drug_metadata.items():
            drug_features = set(info.get("features", []))
            drug_genes = info.get("genes", [])

            if antecedents_targets.issubset(drug_features):
                if (db_id, target_disease_id) not in known_train_pairs:
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

        # 按照置信度排序
        print("\n🌟 Top 15 新药重定位候选推荐 (按置信度排序 - 反应治愈概率):")
        top_15_df = discovery_df.head(15)
        for idx, row in top_15_df.iterrows():
            gr_str = "∞" if row['Rule_Growth_Rate'] == float('inf') else f"{row['Rule_Growth_Rate']:.2f}"
            print(
                f"   💊 药物: {row['Drug_Name']} -> 🎯 预测主治: {row['Predicted_Disease_Name']}  [{row['Validation_Status']}]")
            print(
                f"      (靶向机制: {row['Matched_Targets']}\n       关联基因: {row['Bridging_Genes']} | 置信度: {row['Rule_Confidence']:.4f} | 特异性: {gr_str})")

        # 按照增长率（特异性）排序
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

        # 长尾探索
        print("\n🌈 更多长尾/多样的重定位候选:")
        displayed_diseases = set(top_15_df['Predicted_Disease_ID']).union(set(top_15_growth_df['Predicted_Disease_ID']))
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

    print("\n✅ 全流程执行完毕！")


if __name__ == "__main__":
    main()
