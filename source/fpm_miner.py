import gc
import os
import time
from collections import Counter

import pandas as pd
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder


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
            filtered_t = [item for item in t if item in valid_items]
            if len(filtered_t) >= 2:
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
            def has_disease(frozen_set):
                return any(str(item).startswith("DISEASE_") for item in frozen_set)

            rules['is_disease_target'] = rules['consequents'].apply(has_disease)
            target_rules = rules[rules['is_disease_target'] == True].copy()
            target_rules = target_rules.sort_values(by="lift", ascending=False)

            rule_file = os.path.join(self.output_dir, "association_rules_train.csv")
            target_rules.to_csv(rule_file, index=False, encoding='utf-8-sig')

            return target_rules
        else:
            return None
