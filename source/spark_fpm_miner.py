import os
import time

import pandas as pd
from pyspark.ml.fpm import FPGrowth
from pyspark.sql.functions import col, udf
from pyspark.sql.types import BooleanType


class RuleRefiner:
    @staticmethod
    def remove_redundant_rules(rules_df, conf_tol=0.01, supp_tol=0.002, gr_tol=1.0):
        if rules_df is None or rules_df.empty:
            return rules_df

        retained_indices = []
        rules_df['gr_num'] = rules_df['growth_rate'].apply(lambda x: 999999 if x == float('inf') else x)

        for disease, group in rules_df.groupby('consequents'):
            group = group.assign(ant_len=group['antecedents'].apply(len)).sort_values(by='ant_len', ascending=True)
            retained_for_disease = []

            for idx, row in group.iterrows():
                ant_set = set(row['antecedents'])
                is_redundant = False

                for r_idx, r_row in retained_for_disease:
                    if set(r_row['antecedents']).issubset(ant_set):
                        diff_conf = abs(row['confidence'] - r_row['confidence'])
                        diff_supp = abs(row['support'] - r_row['support'])
                        diff_gr = abs(row['gr_num'] - r_row['gr_num'])
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
        if rules_df is None or rules_df.empty: return rules_df
        diverse_rules = []
        disease_counts = {}
        sorted_df = rules_df.sort_values(by=['growth_rate', 'lift'], ascending=[False, False])
        for idx, row in sorted_df.iterrows():
            cons = list(row['consequents'])[0]
            count = disease_counts.get(cons, 0)
            if count < max_per_disease:
                diverse_rules.append(row)
                disease_counts[cons] = count + 1
            if len(diverse_rules) >= top_n: break
        return pd.DataFrame(diverse_rules)

    @staticmethod
    def extract_representative_rules(rules_df, w1=100, w2=2.0, w3=2000):
        if rules_df is None or rules_df.empty: return rules_df
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


class SparkFPMMiner:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def mine_rules(self, df_transactions, min_support=0.01, min_confidence=0.15):
        print(f"\n[Spark挖掘机] 启动分布式关联规则挖掘 (基于 PySpark MLlib)...")
        start_time = time.time()

        fpGrowth = FPGrowth(itemsCol="items", minSupport=min_support, minConfidence=min_confidence)

        print("[Spark挖掘机] 正在构建分布式 FP-Tree 并挖掘频繁项集...(交由 Spark 引擎计算)")
        model = fpGrowth.fit(df_transactions)

        rules = model.associationRules

        fp_time = time.time() - start_time
        print(f"[性能展示] Spark MLlib 分布式计算核心耗时: {fp_time:.4f} 秒")

        if rules.count() > 0:
            def is_strict_spark_rule(antecedent, consequent):
                if not antecedent or not consequent:
                    return False
                for item in antecedent:
                    if str(item).startswith("DISEASE_"):
                        return False
                if len(consequent) != 1:
                    return False
                if not str(consequent[0]).startswith("DISEASE_"):
                    return False
                return True

            strict_rule_udf = udf(is_strict_spark_rule, BooleanType())
            target_rules = rules.filter(strict_rule_udf(col("antecedent"), col("consequent")))

            print("[Spark挖掘机] 正在将严格过滤后的规则映射回 Pandas 格式...")
            target_rules_pd = target_rules.toPandas()

            target_rules_pd.rename(columns={'antecedent': 'antecedents', 'consequent': 'consequents'}, inplace=True)
            target_rules_pd['antecedents'] = target_rules_pd['antecedents'].apply(frozenset)
            target_rules_pd['consequents'] = target_rules_pd['consequents'].apply(frozenset)

            target_rules_pd = target_rules_pd.sort_values(by="lift", ascending=False)

            rule_file = os.path.join(self.output_dir, "spark_association_rules_train.csv")
            target_rules_pd.to_csv(rule_file, index=False, encoding='utf-8-sig')

            return target_rules_pd
        else:
            return None
