import time

from tqdm import tqdm


class TransactionBuilder:
    def __init__(self, drug_metadata):
        self.drug_metadata = drug_metadata

    def build_transactions(self, df):
        print(f"\n[构建器] 开始基于全量数据构建 Transaction 事务集...")
        time.sleep(1)

        transactions = []
        pbar = tqdm(total=len(df), desc="构建事务", unit="row")

        for _, row in df.iterrows():
            db_id = row['drugbank_id']
            disease_id = row['ind_id']

            drug_features = self.drug_metadata.get(db_id, {}).get("features", [])

            transaction = [f"DRUG_{db_id}"] + drug_features + [f"DISEASE_{disease_id}"]
            transactions.append(transaction)
            pbar.update(1)

        pbar.close()
        print(f"[构建器] 构建完成！共生成 {len(transactions)} 条极其干净的事务记录。")
        return transactions
