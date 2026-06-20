import os
import time

from pyspark.ml.fpm import FPGrowth
from pyspark.sql.functions import col, udf
from pyspark.sql.types import BooleanType


class SparkFPMMiner:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def mine_rules(self, df_transactions, min_support=0.01, min_confidence=0.15):
        print(f"\n[Spark挖掘机] 启动分布式关联规则挖掘 (基于 PySpark MLlib)...")
        start_time = time.time()

        # 初始化 Spark FPGrowth 模型
        fpGrowth = FPGrowth(itemsCol="items", minSupport=min_support, minConfidence=min_confidence)

        print("[Spark挖掘机] 正在构建分布式 FP-Tree 并挖掘频繁项集...(交由 Spark 引擎计算)")
        model = fpGrowth.fit(df_transactions)

        # 获取关联规则 DataFrame (包含 antecedent, consequent, confidence, lift, support)
        rules = model.associationRules

        fp_time = time.time() - start_time
        print(f"[性能展示] Spark MLlib 分布式计算核心耗时: {fp_time:.4f} 秒")

        if rules.count() > 0:
            # 过滤规则：后件必须包含疾病 (DISEASE_)
            def has_disease(consequents):
                return any(str(item).startswith("DISEASE_") for item in consequents)

            disease_udf = udf(has_disease, BooleanType())
            target_rules = rules.filter(disease_udf(col("consequent")))

            print("[Spark挖掘机] 正在将分布式规则映射回 Pandas 格式，以兼容下游自定义指标分析...")
            # 将 Spark DataFrame 拉回本地驱动器转换为 Pandas DataFrame
            target_rules_pd = target_rules.toPandas()

            # 字段重命名并转换数据类型
            target_rules_pd.rename(columns={'antecedent': 'antecedents', 'consequent': 'consequents'}, inplace=True)
            target_rules_pd['antecedents'] = target_rules_pd['antecedents'].apply(frozenset)
            target_rules_pd['consequents'] = target_rules_pd['consequents'].apply(frozenset)

            # 按提升度降序排列
            target_rules_pd = target_rules_pd.sort_values(by="lift", ascending=False)

            rule_file = os.path.join(self.output_dir, "spark_association_rules_train.csv")
            target_rules_pd.to_csv(rule_file, index=False, encoding='utf-8-sig')

            return target_rules_pd
        else:
            return None
