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
* 来源：https://unmtid-shinyapps.net/shiny/repodb/
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

## 📂 4. 项目结构

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
├── 📁 source/                            # 源代码目录
│   ├── 🧾 data_parser.py                 # 数据解析模块
│   ├── 🧾 transaction_builder.py         # 事务集构建模块
│   ├── 🧾 fpm_miner.py                   # FP-Growth 关联规则挖掘模块
│   └── 🚀 main.py                        # 主程序与调度中心
├── 👀 README.md                          # README
└── 📜 requirements.txt                   # 依赖列表
```

---

## 📈 5. 预期结果

```text
🏆 Top 10 高特异性关联规则 (Emerging Patterns):
   前件: TARGET_Angiotensin-converting_enzyme -> 后件: 【Hypertensive disease】
       (Support: 0.0024, Confidence: 0.4884, Lift: 37.93, GrowthRate: ∞ (纯正向))
   前件: TARGET_Gag-Pol_polyprotein -> 后件: 【HIV Infections】
       (Support: 0.0036, Confidence: 0.7442, Lift: 184.62, GrowthRate: 16.58)
   前件: TARGET_Reverse_transcriptase/RNaseH -> 后件: TARGET_Gag-Pol_polyprotein, 【HIV Infections】
       (Support: 0.0021, Confidence: 0.7917, Lift: 220.95, GrowthRate: 9.84)
   前件: TARGET_Gag-Pol_polyprotein -> 后件: TARGET_Reverse_transcriptase/RNaseH, 【HIV Infections】
       (Support: 0.0021, Confidence: 0.4419, Lift: 207.70, GrowthRate: 9.84)
   前件: TARGET_Reverse_transcriptase/RNaseH, TARGET_Gag-Pol_polyprotein -> 后件: 【HIV Infections】
       (Support: 0.0021, Confidence: 0.8261, Lift: 204.94, GrowthRate: 9.84)
   前件: TARGET_Reverse_transcriptase/RNaseH -> 后件: 【HIV Infections】
       (Support: 0.0021, Confidence: 0.7917, Lift: 196.40, GrowthRate: 9.84)

🚀 系统成功挖掘出 182 条全新潜在重定位关联！
🌟 Top 15 新药重定位候选推荐 (按置信度排序):
   💊 药物: Dexelvucitabine -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Reverse_transcriptase/RNaseH
       关联基因: 无直接重合(间接机制) | 置信度: 0.7917 | 特异性: 9.84)
   💊 药物: Racivir -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Reverse_transcriptase/RNaseH
       关联基因: 无直接重合(间接机制) | 置信度: 0.7917 | 特异性: 9.84)
   💊 药物: 5-[(5-fluoro-3-methyl-1H-indazol-4-yl)oxy]benzene-1,3-dicarbonitrile -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Reverse_transcriptase/RNaseH
       关联基因: 无直接重合(间接机制) | 置信度: 0.7917 | 特异性: 9.84)
   💊 药物: Sennosides -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Reverse_transcriptase/RNaseH
       关联基因: AQP3 | 置信度: 0.7917 | 特异性: 9.84)
   💊 药物: (3S)-Tetrahydro-3-furanyl {(2S,3S)-4-[(2S,4R)-4-{(1S,2R)-2-[(S)-amino(hydroxy)methoxy]-2,3-dihydro-1H-inden-1-yl}-2-benzyl-3-oxo-2-pyrrolidinyl]-3-hydroxy-1-phenyl-2-butanyl}carbamate -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 无直接重合(间接机制) | 置信度: 0.7442 | 特异性: 16.58)
   💊 药物: N,N-[2,5-O-Dibenzyl-glucaryl]-DI-[1-amino-indan-2-OL] -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 无直接重合(间接机制) | 置信度: 0.7442 | 特异性: 16.58)
   💊 药物: (4R,5S,6S,7R)-1,3-dibenzyl-4,7-bis(phenoxymethyl)-5,6-dihydroxy-1,3 diazepan-2-one -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 无直接重合(间接机制) | 置信度: 0.7442 | 特异性: 16.58)
   💊 药物: N-[2-hydroxy-1-indanyl]-5-[(2-tertiarybutylaminocarbonyl)-4(benzo[1,3]dioxol-5-ylmethyl)-piperazino]-4-hydroxy-2-(1-phenylethyl)-pentanamide -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 无直接重合(间接机制) | 置信度: 0.7442 | 特异性: 16.58)
   💊 药物: (2S)-1-[(2S,4R)-4-Benzyl-2-hydroxy-5-{[(1S,2R,5S)-2-hydroxy-5-methylcyclopentyl]amino}-5-oxopentyl]-4-{[6-chloro-5-(4-methyl-1-piperazinyl)-2-pyrazinyl]carbonyl}-N-(2-methyl-2-propanyl)-2-piperazineca rboxamide -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 无直接重合(间接机制) | 置信度: 0.7442 | 特异性: 16.58)
   💊 药物: Tert-Butyloxycarbonyl Group -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 无直接重合(间接机制) | 置信度: 0.7442 | 特异性: 16.58)
   💊 药物: SD146 -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 无直接重合(间接机制) | 置信度: 0.7442 | 特异性: 16.58)
   💊 药物: (2R,3R,4R,5R)-3,4-Dihydroxy-N,N'-bis[(1S,2R)-2-hydroxy-2,3-dihydro-1H-inden-1-yl]-2,5-bis(2-phenylethyl)hexanediamide -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 无直接重合(间接机制) | 置信度: 0.7442 | 特异性: 16.58)
   💊 药物: XV638 -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 无直接重合(间接机制) | 置信度: 0.7442 | 特异性: 16.58)
   💊 药物: Inhibitor Bea428 -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 无直接重合(间接机制) | 置信度: 0.7442 | 特异性: 16.58)
   💊 药物: JE-2147 -> 🎯 预测主治: HIV Infections
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 无直接重合(间接机制) | 置信度: 0.7442 | 特异性: 16.58)

🌈 更多长尾/多样的重定位候选 (消除头部霸屏，展示不同病种):
   💊 药物: Alacepril -> 🎯 预测主治: Hypertensive disease
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 无直接重合(间接机制) | 置信度: 0.4884 | 特异性: ∞)
```
