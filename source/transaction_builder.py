import time

from tqdm import tqdm


class TransactionBuilder:
    def __init__(self, drug_metadata, disease_to_genes):
        self.drug_metadata = drug_metadata
        self.disease_to_genes = disease_to_genes

    # 将传入的 csv_filepath 改为直接传入 DataFrame (df)
    def build_transactions(self, df):
        """
        将 DataFrame 转化为异构事务集:
        Transaction = [DrugBankID, *Targets, DiseaseID]
        """
        print(f"\n[构建器] 开始基于全量数据构建 Transaction 事务集...")
        time.sleep(1)  # 为了输出的异步同步

        transactions = []
        pbar = tqdm(total=len(df), desc="构建事务", unit="row")

        for _, row in df.iterrows():
            db_id = row['drugbank_id']
            disease_id = row['ind_id']

            drug_features = self.drug_metadata.get(db_id, {}).get("features", [])

            ctd_query_id = disease_id if str(disease_id).startswith("MESH:") else f"MESH:{disease_id}"
            disease_genes = self.disease_to_genes.get(ctd_query_id, [])

            transaction = [f"DRUG_{db_id}"] + drug_features + [f"DISEASE_{disease_id}"]
            transactions.append(transaction)
            pbar.update(1)

        pbar.close()
        print(f"[构建器] 构建完成！共生成 {len(transactions)} 条事务记录。")
        return transactions
