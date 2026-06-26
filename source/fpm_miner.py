import gc
import os
import time
from collections import Counter

import pandas as pd
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder


class RuleRefiner:

    @staticmethod
    def remove_redundant_rules(rules_df, conf_tol=0.01, supp_tol=0.002, gr_tol=1.0):
        if rules_df is None or rules_df.empty:
            return rules_df

        retained_indices = []
        rules_df['gr_num'] = rules_df['growth_rate'].apply(lambda x: 999999 if x == float('inf') else x)

        for disease, group in rules_df.groupby('consequents'):
            # 按前件长度升序排序，优先保留简短且泛化性强的机制
            group = group.assign(ant_len=group['antecedents'].apply(len)).sort_values(by='ant_len', ascending=True)
            retained_for_disease = []

            for idx, row in group.iterrows():
                ant_set = set(row['antecedents'])
                is_redundant = False

                for r_idx, r_row in retained_for_disease:
                    # 如果当前已保留的规则是新规则的子集 (例如 A+B 是 A+B+C 的子集)
                    if set(r_row['antecedents']).issubset(ant_set):
                        diff_conf = abs(row['confidence'] - r_row['confidence'])
                        diff_supp = abs(row['support'] - r_row['support'])
                        diff_gr = abs(row['gr_num'] - r_row['gr_num'])

                        # 如果各项生物学统计指标差异极小，说明新增的特征是冗余的“搭便车”特征
                        if diff_conf <= conf_tol and diff_supp <= supp_tol and (diff_gr <= gr_tol or (
                                row['growth_rate'] == float('inf') and r_row['growth_rate'] == float('inf'))):
                            is_redundant = True
                            break

                if not is_redundant:
                    retained_for_disease.append((idx, row))
                    retained_indices.append(idx)

        clean_df = rules_df.loc[retained_indices].copy()
        clean_df.drop(columns=['gr_num', 'ant_len'], inplace=True, errors='ignore')
        return clean_df

    @staticmethod
    def get_diverse_top_rules(rules_df, top_n=10, max_per_disease=2):
        if rules_df is None or rules_df.empty:
            return rules_df

        diverse_rules = []
        disease_counts = {}
        sorted_df = rules_df.sort_values(by=['growth_rate', 'lift'], ascending=[False, False])

        for idx, row in sorted_df.iterrows():
            cons = list(row['consequents'])[0]
            count = disease_counts.get(cons, 0)

            if count < max_per_disease:
                diverse_rules.append(row)
                disease_counts[cons] = count + 1

            if len(diverse_rules) >= top_n:
                break

        return pd.DataFrame(diverse_rules)

    @staticmethod
    def extract_representative_rules(rules_df, w1=100, w2=2.0, w3=2000):
        if rules_df is None or rules_df.empty:
            return rules_df

        # 防止 GrowthRate 里的 inf 爆炸，将其锚定为最大有效值的 1.5 倍
        valid_gr = rules_df[rules_df['growth_rate'] != float('inf')]['growth_rate']
        max_valid_gr = valid_gr.max() if not valid_gr.empty else 10.0
        inf_gr_val = max_valid_gr * 1.5

        def calc_score(row):
            gr = inf_gr_val if row['growth_rate'] == float('inf') else row['growth_rate']
            return (row['confidence'] * w1) + (gr * w2) + (row['support'] * w3)

        rules_df_copy = rules_df.copy()
        rules_df_copy['rep_score'] = rules_df_copy.apply(calc_score, axis=1)

        rep_indices = []
        for disease, group in rules_df_copy.groupby('consequents'):
            rep_indices.append(group['rep_score'].idxmax())

        return rules_df_copy.loc[rep_indices].sort_values(by='rep_score', ascending=False)


class FPMMiner:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def mine_rules(self, transactions, min_support=0.01, min_confidence=0.5):
        print(f"\n[挖掘机] 启动全量数据关联规则挖掘...")
        start_time = time.time()

        print("[挖掘机] 正在执行前置项集频率剪枝...")
        num_trans = len(transactions)
        min_count = min_support * num_trans

        # 1. 统计所有单项的出现次数
        item_counts = Counter(item for t in transactions for item in t)

        # 2. 过滤掉连单项 support 都达不到的特征 (它们绝对不可能构成频繁项集)
        valid_items = {item for item, count in item_counts.items() if count >= min_count}

        # 3. 重建事务集，并剔除长度 < 2 的无效事务（无法构成 A->B 规则）
        pruned_transactions = []
        for t in transactions:
            # 过滤出当前事务中满足 support 阈值的有效项
            filtered_t = [item for item in t if item in valid_items]

            # 显式判断：剪枝后的事务中是否还保留着疾病标签
            has_disease = any(str(item).startswith("DISEASE_") for item in filtered_t)

            # 只有长度大于等于2，且包含疾病标签的事务，才允许进入 FP-Tree
            if len(filtered_t) >= 2 and has_disease:
                pruned_transactions.append(filtered_t)

        print(f"[挖掘机] 剪枝完成！有效词表大小从 {len(item_counts)} 缩减至 {len(valid_items)}")
        print(f"[挖掘机] 有效事务数从 {num_trans} 缩减至 {len(pruned_transactions)}")

        if len(pruned_transactions) == 0:
            print("[警告] 剪枝后无有效事务，请尝试调低 min_support。")
            return None

        # 内存释放
        del transactions
        del item_counts
        gc.collect()

        print("[挖掘机] 正在构建轻量级稀疏矩阵...(这会花点时间)")
        te = TransactionEncoder()
        te_ary = te.fit(pruned_transactions).transform(pruned_transactions, sparse=True)

        del pruned_transactions  # 再次释放
        gc.collect()

        sparse_df = pd.DataFrame.sparse.from_spmatrix(te_ary, columns=te.columns_)
        del te_ary
        gc.collect()

        print("[挖掘机] 正在构建 FP-Tree...(这会花点时间)")
        fp_start = time.time()
        freq_items = fpgrowth(
            sparse_df,
            min_support=min_support,
            use_colnames=True,
            max_len=4
        )
        fp_time = time.time() - fp_start
        print(f"[性能展示] FP-Growth 核心耗时: {fp_time:.4f} 秒")

        itemset_count = len(freq_items)
        print(f"[挖掘机] 成功挖掘出 {itemset_count} 个频繁项集。")

        if itemset_count > 1000000:
            print(f"[致命警告] 频繁项集数量极其庞大！触发安全熔断。")
            del sparse_df, freq_items
            gc.collect()
            return None

        print("[挖掘机] 正在生成关联规则...(这会花点时间)")
        rules = association_rules(freq_items, metric="confidence", min_threshold=min_confidence)

        del sparse_df, freq_items
        gc.collect()

        total_time = time.time() - start_time
        print(f"[性能展示] 事务映射 + 挖掘全流程总耗时: {total_time:.4f} 秒")

        if len(rules) > 0:
            # 只允许 TARGET -> DISEASE)
            def strict_rule_filter(row):
                ants = row['antecedents']
                cons = row['consequents']

                # 条件 1: 前件 (antecedents) 绝对不能包含疾病 (DISEASE_)
                if any(str(item).startswith("DISEASE_") for item in ants):
                    return False

                # 条件 2: 后件 (consequents) 必须严格只有 1 个项目
                if len(cons) != 1:
                    return False

                # 条件 3: 后件唯一的这个项目，必须是疾病 (DISEASE_)
                if not list(cons)[0].startswith("DISEASE_"):
                    return False

                return True

            rules['is_strict_valid'] = rules.apply(strict_rule_filter, axis=1)
            target_rules = rules[rules['is_strict_valid'] == True].copy()
            target_rules.drop(columns=['is_strict_valid'], inplace=True)

            target_rules = target_rules.sort_values(by="lift", ascending=False)

            rule_file = os.path.join(self.output_dir, "association_rules_train.csv")
            target_rules.to_csv(rule_file, index=False, encoding='utf-8-sig')

            return target_rules
        else:
            return None
