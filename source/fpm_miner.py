import gc
import os
import time

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

        # 1. 稀疏矩阵转换
        te = TransactionEncoder()
        te_ary = te.fit(transactions).transform(transactions, sparse=True)
        sparse_df = pd.DataFrame.sparse.from_spmatrix(te_ary, columns=te.columns_)

        gc.collect()

        # 2. 频繁项集挖掘
        print("[挖掘机] 正在构建 FP-Tree...")
        fp_start = time.time()
        freq_items = fpgrowth(
            sparse_df,
            min_support=min_support,
            use_colnames=True,
            max_len=4  # 已调整为 4，捕捉 3靶点 -> 1疾病 的高级联动机制
        )
        fp_time = time.time() - fp_start
        print(f"[性能展示] FP-Growth 核心耗时: {fp_time:.4f} 秒")

        itemset_count = len(freq_items)
        print(f"[挖掘机] 成功挖掘出 {itemset_count} 个频繁项集。")

        if itemset_count == 0:
            print("[警告] 频繁项集为0！请尝试稍微调低 min_support")
            return None

        # 【安全熔断机制】 若频繁项集因为支持度太低而超过 100 万个，直接拦截，防止后续 association_rules 卡死
        if itemset_count > 1000000:
            print(f"[致命警告] 当前挖掘出的频繁项集数量极其庞大！")
            print("[信息] 为保护您的内存不被撑爆，系统已触发安全熔断。")
            print("[解决方案] 请在 main.py 中将 min_support 调高 (调到大于 0.0016) 后重试！")
            return None

        # 3. 生成关联规则
        print("[挖掘机] 正在生成关联规则...")
        rules = association_rules(freq_items, metric="confidence", min_threshold=min_confidence)

        total_time = time.time() - start_time
        print(f"[性能展示] 事务映射 + 挖掘全流程总耗时: {total_time:.4f} 秒")

        if len(rules) > 0:
            def has_disease(frozen_set):
                return any(str(item).startswith("DISEASE_") for item in frozen_set)

            rules['is_disease_target'] = rules['consequents'].apply(has_disease)
            target_rules = rules[rules['is_disease_target'] == True].copy()
            target_rules = target_rules.sort_values(by="lift", ascending=False)

            # 【核心修复点】：添加 encoding='utf-8-sig'，彻底解决 Excel 打开乱码的问题
            rule_file = os.path.join(self.output_dir, "association_rules.csv")
            target_rules.to_csv(rule_file, index=False, encoding='utf-8-sig')

            return target_rules
        else:
            return None
