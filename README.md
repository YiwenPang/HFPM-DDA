# **HFPM-DDA**：**H**eterogeneous **F**requent **P**attern **M**ining for **D**rug-**D**isease **A**ssociation (基于异构频繁模式挖掘的药物-疾病关联网络)

这是一份大数据分析与挖掘课程的作业，利用关联规则算法，实现了**高特异性关联规则发现**，**新药重定位候选推荐**,也提供了**更多长尾/多样的重定位候选**.

---

## 📊 1. 数据集来源 (Data Sources)

由于版权限制，数据不包含在内，请从官方渠道下载。

Data is not included due to licensing restrictions. Please download from official sources.

请在运行前将数据放入 `data/` 目录：

### DrugBank 数据库

* 文件：`drugbank_all_full_database.xml`
* 来源：https://go.drugbank.com/releases/latest
* 作用：提取药物的基因靶点信息

### CTD 数据库

* 文件：`CTD_genes_diseases.tsv`
* 来源：http://ctdbase.org/downloads/
* 作用：提供疾病-基因关联数据
* 注意：此数据库的数据位置可能会发生变化，要格外留意，必要时打开查看。

### repoDB 数据库

* 文件：`repoDB_full.csv`
* 来源：https://go.drugbank.com/releases/latest
* 作用：提供可靠的药物-疾病关联对

---

## 💻 2. 环境配置 (Environment Setup)

本项目所使用计算机硬件和软件配置如下：

硬件配置：

* Intel® Core™ Ultra 9 Processor 285K (Arrow Lake)
* NVIDIA® GeForce RTX 5080 (16GB GDDR7)
* 64 GB (2 × 32 GB DDR5)

软件配置：
* Microsoft Windows 11 Pro for Workstations
* Python 3.12
* PyCharm 2026.1

推荐使用 Conda 3.12，建议使用虚拟环境。

### 安装依赖包

```bash
pip install -r requirements.txt
```

---

## 🏃 3. 运行方式
直接执行：
```bash
cd source
python main.py
```
即可。

---

## 📂 6. 项目结构

```text
📦 HFPM-DDA/
├── 📁 data/                              # 原始数据
│   ├── 🧬 ctd_genes_diseases_schema.json # 自己生成的 CTD JSON 结构定义（无需创建）
│   ├── 💾 CTD_genes_diseases.tsv         # CTD 数据库
│   ├── 🧬 drugbank.xsd                   # DrugBank XML 结构定义（无需下载）
│   ├── 💾 drugbank_all_full_database.xml # DrugBank 数据库
│   └── ⛓️ repoDB_full.csv                # repoDB 数据库
├── 📁 output/                            # 输出结果
│   ├── 🧾 new_drug_discoveries.csv       # 新药发现候选清单
│   └── 🧠 association_rules.csv          # 关联规则库
├── 📁 source/                            # 输出结果
│   ├── 🧾 data_parser.py                 # 数据解析模块
│   ├── 🧾 transaction_builder.py         # 事务集构建模块
│   ├── 🧾 fpm_miner.py                   # FP-Growth 关联规则挖掘模块
│   └── 🚀 main.py                        # 主程序与调度中心
├── 👀 README.md                          # README
└── 📜 requirements.txt                   # 依赖列表
```

---

## 📈 7. 预期结果

```text
🏆 Top 10 高特异性关联规则 (Emerging Patterns):
   前件: TARGET_Coagulation_factor_IX -> 后件: TARGET_Coagulation_factor_X, 【Hemophilia A】
       (Support: 0.0007, Confidence: 0.7500, Lift: 956.89, GrowthRate: ∞ (纯正向))
   前件: TARGET_Spike_glycoprotein -> 后件: 【COVID19 (disease)】
       (Support: 0.0009, Confidence: 1.0000, Lift: 744.25, GrowthRate: ∞ (纯正向))
   前件: TARGET_Coagulation_factor_X, TARGET_Coagulation_factor_IX -> 后件: 【Hemophilia A】
       (Support: 0.0007, Confidence: 0.7500, Lift: 608.93, GrowthRate: ∞ (纯正向))
   前件: TARGET_Coagulation_factor_IX -> 后件: 【Hemophilia A】
       (Support: 0.0007, Confidence: 0.7500, Lift: 608.93, GrowthRate: ∞ (纯正向))
   前件: TARGET_Protein_P -> 后件: 【Hepatitis B, Chronic】
       (Support: 0.0007, Confidence: 0.7500, Lift: 558.19, GrowthRate: ∞ (纯正向))
   前件: TARGET_von_Willebrand_factor -> 后件: 【Hemophilia A】
       (Support: 0.0007, Confidence: 0.6667, Lift: 541.27, GrowthRate: ∞ (纯正向))
   前件: TARGET_ATP-sensitive_inward_rectifier_potassium_channel_10 -> 后件: TARGET_ATP-binding_cassette_sub-family_C_member_8, 【Diabetes Mellitus, Non-Insulin-Dependent】
       (Support: 0.0006, Confidence: 0.7143, Lift: 531.61, GrowthRate: ∞ (纯正向))
   前件: TARGET_Voltage-dependent_L-type_calcium_channel_subunit_beta-2 -> 后件: 【Hypertensive disease】, TARGET_Voltage-dependent_L-type_calcium_channel_subunit_alpha-1D
       (Support: 0.0007, Confidence: 0.4615, Lift: 515.25, GrowthRate: ∞ (纯正向))
   前件: TARGET_Voltage-dependent_L-type_calcium_channel_subunit_alpha-1D -> 后件: 【Hypertensive disease】, TARGET_Voltage-dependent_L-type_calcium_channel_subunit_alpha-1S
       (Support: 0.0008, Confidence: 0.3889, Lift: 496.17, GrowthRate: ∞ (纯正向))
   前件: TARGET_Voltage-dependent_L-type_calcium_channel_subunit_beta-2 -> 后件: 【Hypertensive disease】, TARGET_Voltage-dependent_L-type_calcium_channel_subunit_alpha-1S
       (Support: 0.0006, Confidence: 0.3846, Lift: 490.71, GrowthRate: ∞ (纯正向))

🚀 系统成功挖掘出 341 条全新潜在重定位关联！
🌟 Top 15 新药重定位候选推荐 (按置信度排序):
   💊 药物: Zavegepant -> 🎯 预测主治: Migraine Disorders
      (命中靶向机制: TARGET_Calcitonin_gene-related_peptide_type_1_receptor | 规则置信度: 1.0000 | 特异性: ∞)
   💊 药物: Olcegepant -> 🎯 预测主治: Migraine Disorders
      (命中靶向机制: TARGET_Calcitonin_gene-related_peptide_type_1_receptor | 规则置信度: 1.0000 | 特异性: ∞)
   💊 药物: Atogepant -> 🎯 预测主治: Migraine Disorders
      (命中靶向机制: TARGET_Calcitonin_gene-related_peptide_type_1_receptor | 规则置信度: 1.0000 | 特异性: ∞)
   💊 药物: MK-3207 -> 🎯 预测主治: Migraine Disorders
      (命中靶向机制: TARGET_Calcitonin_gene-related_peptide_type_1_receptor | 规则置信度: 1.0000 | 特异性: ∞)
   💊 药物: Telcagepant -> 🎯 预测主治: Migraine Disorders
      (命中靶向机制: TARGET_Calcitonin_gene-related_peptide_type_1_receptor | 规则置信度: 1.0000 | 特异性: ∞)
   💊 药物: Anti-SARS-CoV-2 REGN-COV2 -> 🎯 预测主治: COVID19 (disease)
      (命中靶向机制: TARGET_Spike_glycoprotein | 规则置信度: 1.0000 | 特异性: ∞)
   💊 药物: Pemivibart -> 🎯 预测主治: COVID19 (disease)
      (命中靶向机制: TARGET_Spike_glycoprotein | 规则置信度: 1.0000 | 特异性: ∞)
   💊 药物: Sipavibart -> 🎯 预测主治: COVID19 (disease)
      (命中靶向机制: TARGET_Spike_glycoprotein | 规则置信度: 1.0000 | 特异性: ∞)
   💊 药物: Bebtelovimab -> 🎯 预测主治: COVID19 (disease)
      (命中靶向机制: TARGET_Spike_glycoprotein | 规则置信度: 1.0000 | 特异性: ∞)
   💊 药物: Raxtozinameran -> 🎯 预测主治: COVID19 (disease)
      (命中靶向机制: TARGET_Spike_glycoprotein | 规则置信度: 1.0000 | 特异性: ∞)
   💊 药物: Bemcentinib -> 🎯 预测主治: COVID19 (disease)
      (命中靶向机制: TARGET_Spike_glycoprotein | 规则置信度: 1.0000 | 特异性: ∞)
   💊 药物: Racivir -> 🎯 预测主治: HIV Infections
      (命中靶向机制: TARGET_Reverse_transcriptase/RNaseH | 规则置信度: 0.7917 | 特异性: 9.84)
   💊 药物: 5-[(5-fluoro-3-methyl-1H-indazol-4-yl)oxy]benzene-1,3-dicarbonitrile -> 🎯 预测主治: HIV Infections
      (命中靶向机制: TARGET_Reverse_transcriptase/RNaseH | 规则置信度: 0.7917 | 特异性: 9.84)
   💊 药物: Sennosides -> 🎯 预测主治: HIV Infections
      (命中靶向机制: TARGET_Reverse_transcriptase/RNaseH | 规则置信度: 0.7917 | 特异性: 9.84)
   💊 药物: Dexelvucitabine -> 🎯 预测主治: HIV Infections
      (命中靶向机制: TARGET_Reverse_transcriptase/RNaseH | 规则置信度: 0.7917 | 特异性: 9.84)

🌈 更多长尾/多样的重定位候选 (消除头部霸屏，展示不同病种):
   💊 药物: Menadione -> 🎯 预测主治: Hemophilia A
      (命中靶向机制: TARGET_Coagulation_factor_IX | 规则置信度: 0.7500 | 特异性: ∞)
   💊 药物: Lotiglipron -> 🎯 预测主治: Diabetes Mellitus, Non-Insulin-Dependent
      (命中靶向机制: TARGET_Glucagon-like_peptide_1_receptor | 规则置信度: 0.7500 | 特异性: 3.11)
   💊 药物: Besifovir dipivoxil -> 🎯 预测主治: Hepatitis B, Chronic
      (命中靶向机制: TARGET_Protein_P | 规则置信度: 0.7500 | 特异性: ∞)
   💊 药物: Quinethazone -> 🎯 预测主治: Hypertensive disease
      (命中靶向机制: TARGET_Solute_carrier_family_12_member_1, TARGET_Carbonic_anhydrase_1 | 规则置信度: 0.6250 | 特异性: ∞)
   💊 药物: Bendroflumethiazide -> 🎯 预测主治: Edema
      (命中靶向机制: TARGET_Solute_carrier_family_12_member_1 | 规则置信度: 0.3636 | 特异性: ∞)
   💊 药物: Darbepoetin alfa -> 🎯 预测主治: Anemia in chronic kidney disease
      (命中靶向机制: TARGET_Erythropoietin_receptor | 规则置信度: 0.3571 | 特异性: ∞)
   💊 药物: Propiomazine -> 🎯 预测主治: Depressive disorder
      (命中靶向机制: TARGET_Muscarinic_acetylcholine_receptor, TARGET_5-hydroxytryptamine_receptor_2A | 规则置信度: 0.3571 | 特异性: ∞)
   💊 药物: Ibandronate -> 🎯 预测主治: Osteitis Deformans
      (命中靶向机制: TARGET_Hydroxylapatite | 规则置信度: 0.3529 | 特异性: ∞)
```
