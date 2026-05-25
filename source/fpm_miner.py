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

        # 记录开始时间，用于性能评估
        start_time = time.time()

        # 1. 稀疏矩阵转换
        te = TransactionEncoder()
        te_ary = te.fit(transactions).transform(transactions, sparse=True)
        sparse_df = pd.DataFrame.sparse.from_spmatrix(te_ary, columns=te.columns_)

        gc.collect()

        # 2. 频繁项集挖掘
        print("[挖掘机] 正在构建 FP-Tree...(将会长时间无输出，可观察内存状态)")
        fp_start = time.time()
        freq_items = fpgrowth(
            sparse_df,
            min_support=min_support,
            use_colnames=True,
            max_len=3  # 强制限制项集最大长度为 3，防止内存爆炸。
        )
        fp_time = time.time() - fp_start
        print(f"[性能展示] FP-Growth 核心耗时: {fp_time:.4f} 秒")

        if len(freq_items) == 0:
            print("[警告] 频繁项集为0！请尝试调低 min_support")
            return None

        # 3. 生成关联规则
        print("[挖掘机] 正在生成关联规则... (将会长时间无输出，可观察内存状态)")
        rules = association_rules(freq_items, metric="confidence", min_threshold=min_confidence)

        total_time = time.time() - start_time
        print(f"[性能展示] 事务映射 + 挖掘全流程总耗时: {total_time:.4f} 秒")

        if len(rules) > 0:
            # 筛选条件：后件必须包含疾病 (确保是一条“推导疾病”的有效规则)
            def has_disease(frozen_set):
                return any(str(item).startswith("DISEASE_") for item in frozen_set)

            rules['is_disease_target'] = rules['consequents'].apply(has_disease)
            target_rules = rules[rules['is_disease_target'] == True].copy()

            # 按提升度(Lift)降序排列，只看最强效的规则
            target_rules = target_rules.sort_values(by="lift", ascending=False)

            # 只导出一个极其干净、没有任何冗余标识的 CSV 结果文件
            rule_file = os.path.join(self.output_dir, "association_rules.csv")
            target_rules.to_csv(rule_file, index=False)

            return target_rules
        else:
            return None
