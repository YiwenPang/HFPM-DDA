import os
import time

import pandas as pd
from lxml import etree as ET
from tqdm import tqdm


class DataParser:
    def __init__(self, data_dir=None):
        if data_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            self.data_dir = os.path.join(project_root, "data")
        else:
            self.data_dir = data_dir
        self.namespace = "{http://www.drugbank.ca}"

    def parse_drugbank_metadata(self):
        xml_path = os.path.join(self.data_dir, "drugbank_all_full_database.xml")
        if not os.path.exists(xml_path):
            import glob
            xml_files = glob.glob(os.path.join(self.data_dir, "*.xml"))
            if xml_files:
                xml_path = xml_files[0]
                print(f"[解析器] 自动使用 XML 文件: {xml_path}")
            else:
                raise FileNotFoundError(f"在 {self.data_dir} 下找不到任何 XML 文件。")

        print("[解析器] 开始流式解析 DrugBank XML 寻找靶点与基因特征... (这会花点时间)")
        time.sleep(1)

        drug_info = {}
        target_tag = f"{self.namespace}drug"
        context = ET.iterparse(xml_path, events=('end',), tag=target_tag)
        pbar = tqdm(desc="正在解析 DrugBank 药物", unit=" drugs")

        for event, elem in context:
            pbar.update(1)

            # 提取 DrugBank ID
            db_id_elem = elem.find(f"{self.namespace}drugbank-id[@primary='true']")
            db_id = db_id_elem.text if db_id_elem is not None else None

            # 提取药物真实名称
            name_elem = elem.find(f"{self.namespace}name")
            drug_name = name_elem.text if (name_elem is not None and name_elem.text) else db_id

            # 提取靶点和隐藏的靶点基因
            targets = []
            target_genes = []

            targets_elem = elem.find(f"{self.namespace}targets")
            if targets_elem is not None:
                for target in targets_elem.findall(f"{self.namespace}target"):
                    # 1. 提取靶点蛋白质名称（用于规则挖掘特征）
                    t_name = target.find(f"{self.namespace}name")
                    if t_name is not None and t_name.text:
                        targets.append(f"TARGET_{t_name.text.replace(' ', '_')}")

                    # 2. 深入提取靶点的基因名称 (Gene Symbol，用于后期关联匹配)
                    for gene_elem in target.iter(f"{self.namespace}gene-name"):
                        if gene_elem is not None and gene_elem.text:
                            target_genes.append(gene_elem.text.upper())  # 统一转大写

            if db_id:
                drug_info[db_id] = {
                    "name": drug_name,
                    "features": targets,
                    "genes": set(target_genes)  # 去重后的药物作用基因集
                }

            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

        pbar.close()
        print(f"[解析器] DrugBank 解析完成，共提取 {len(drug_info)} 种药物属性。")
        return drug_info

    def parse_ctd_genes_diseases(self):
        # 解析 CTD 数据库寻找 DiseaseID 和 Gene 的映射
        tsv_path = os.path.join(self.data_dir, "CTD_genes_diseases.tsv")
        print("[解析器] 正在加载 CTD 基因-疾病数据...（较长时间无输出，但内存在工作）")
        ctd_df = pd.read_csv(tsv_path, sep='\t', comment='#', header=None, low_memory=False)

        ctd_df.columns = ["GeneSymbol", "GeneID", "DiseaseName", "DiseaseID",
                          "DirectEvidence", "InferenceChemicalName", "InferenceScore",
                          "OmimIDs", "PubMedIDs"]

        print("[解析器] 正在将 CTD 数据双重映射为 {DiseaseID/Name: [Genes]} 字典...")

        # 1. ID映射
        disease_to_genes = ctd_df.groupby("DiseaseID")["GeneSymbol"].apply(
            lambda x: [f"GENE_{g}" for g in x.dropna().unique()]
        ).to_dict()

        # 2. 名字映射 (兜底机制)
        name_to_genes = ctd_df.groupby("DiseaseName")["GeneSymbol"].apply(
            lambda x: [f"GENE_{g}" for g in x.dropna().unique()]
        ).to_dict()

        # 将小写的名称映射合并进去
        for name, genes in name_to_genes.items():
            disease_to_genes[str(name).lower()] = genes

        # 提取疾病ID到真实名称的映射字典
        disease_names = ctd_df.drop_duplicates(subset=["DiseaseID"]).set_index("DiseaseID")["DiseaseName"].to_dict()

        print(f"[解析器] CTD 映射完成，涉及疾病库规模: {len(disease_to_genes)}")
        return disease_to_genes, disease_names
