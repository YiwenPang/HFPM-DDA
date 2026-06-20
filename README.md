# **HFPM-DDA**：**H**eterogeneous **F**requent **P**attern **M**ining for **D**rug-**D**isease **A**ssociation (基于异构频繁模式挖掘的药物-疾病关联网络)

这是一份大数据分析与挖掘课程的作业，利用关联规则算法，实现了**高特异性关联规则发现**，**新药重定位候选推荐**,也提供了**更多长尾/多样的重定位候选**.

---

## 📊 1. 数据集来源 (Data Sources)

由于版权限制，数据不包含在内，请从官方渠道下载。

Data is not included due to licensing restrictions. Please download from official sources.

本项目使用来自 DrugBank、CTD 和 repoDB 的数据，仅用于非商业性学术研究。

This project utilizes data from DrugBank, CTD, and repoDB for non-commercial academic research purposes only.

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
├── 📁 data/                                 # 原始数据
│   ├── 🧬 ctd_genes_diseases_schema.json    # 自己生成的 CTD JSON 结构定义（无需创建）
│   ├── 💾 CTD_genes_diseases.tsv            # CTD 数据库
│   ├── 🧬 drugbank.xsd                      # DrugBank XML 结构定义（无需下载）
│   ├── 💾 drugbank_all_full_database.xml    # DrugBank 数据库
│   └── ⛓️ repoDB_full.csv                   # repoDB 数据库
├── 📁 output/                               # 输出结果
│   ├── 🧾 train_approved.csv                # 成功药训练集
│   ├── 🧾 train_failed.csv                  # 失败药训练集
│   ├── 🧾 test_approved.csv                 # 成功药测试集
│   ├── 🧾 test_failed.csv                   # 失败药测试集
│   ├── 🧾 new_drug_discoveries.csv          # 新药预测清单
│   ├── 🧠 association_rules_train.csv       # 关联规则结果
│   ├── 🧾 spark_train_approved.csv          # Apache Spark 版本成功药训练集
│   ├── 🧾 spark_train_failed.csv            # Apache Spark 版本失败药训练集
│   ├── 🧾 spark_test_approved.csv           # Apache Spark 版本成功药测试集
│   ├── 🧾 spark_test_failed.csv             # Apache Spark 版本失败药测试集
│   ├── 🧾 spark_new_drug_discoveries.csv    # Apache Spark 版本新药预测清单
│   └── 🧠 spark_association_rules_train.csv # Apache Spark 版本关联规则结果
├── 📁 source/                               # 源代码目录
│   ├── 🧾 data_parser.py                    # 数据解析模块
│   ├── 🧾 transaction_builder.py            # 事务集构建模块
│   ├── 🧾 fpm_miner.py                      # FP-Growth 关联规则挖掘模块
│   ├── 🚀 main.py                           # 主程序与调度中心
│   ├── 🧾 spark_fpm_miner.py                # Apache Spark 版本 FP-Growth 关联规则挖掘模块
│   └── 🚀 spark_main.py                     # Apache Spark 版本主程序与调度中心
├── 👀 README.md                             # README
└── 📜 requirements.txt                      # 依赖列表
```

---

## 📈 5. 预期结果

```text
============================================================
🚀 欢迎启动 HFPM-DDA 关联规则深度挖掘与新药发现系统 🚀
============================================================

--- [Phase 1: 异构数据流式加载] ---
[解析器] 开始流式解析 DrugBank XML 寻找靶点与基因特征... (这会花点时间)
正在解析 DrugBank 药物: 3963135 drugs [00:40, 97680.37 drugs/s]
[解析器] DrugBank 解析完成，共提取 19857 种药物属性。
[解析器] 正在加载 CTD 基因-疾病数据...(这会花点时间)
[解析器] 开始分块流式吞吐 CTD 数据(这会花点时间)，每块吞吐量: 5000000 行...
  -> 已处理完第 1 个数据块...
  -> 已处理完第 2 个数据块...
  -> 已处理完第 3 个数据块...
  -> 已处理完第 4 个数据块...
  -> 已处理完第 5 个数据块...
  -> 已处理完第 6 个数据块...
  -> 已处理完第 7 个数据块...
  -> 已处理完第 8 个数据块...
  -> 已处理完第 9 个数据块...
  -> 已处理完第 10 个数据块...
  -> 已处理完第 11 个数据块...
  -> 已处理完第 12 个数据块...
  -> 已处理完第 13 个数据块...
  -> 已处理完第 14 个数据块...
  -> 已处理完第 15 个数据块...
  -> 已处理完第 16 个数据块...
  -> 已处理完第 17 个数据块...
  -> 已处理完第 18 个数据块...
  -> 已处理完第 19 个数据块...
  -> 已处理完第 20 个数据块...
  -> 已处理完第 21 个数据块...
  -> 已处理完第 22 个数据块...
  -> 已处理完第 23 个数据块...
  -> 已处理完第 24 个数据块...
  -> 已处理完第 25 个数据块...
[解析器] 正在合并映射...
[解析器] CTD 映射完成，最终浓缩疾病库规模: 14515

--- [Phase 2: 加载全量临床数据 & 构建对比集] ---
[数据] 成功(Approved)记录: 8931 条
[数据] 失败(Terminated/Withdrawn等)记录: 4627 条

--- [Phase 2.5: 数据集切分 (80% 训练集 / 20% 测试集)] ---
[划分] 训练集(Approved): 7144 条已写入硬盘 | 测试集(Approved): 1787 条已写入硬盘

--- [Phase 3: 对比事务映射构建] ---
[构建 训练集 Approved 事务集]

[构建器] 开始基于全量数据构建 Transaction 事务集...
构建事务: 100%|██████████| 7144/7144 [00:00<00:00, 56942.49row/s]
[构建器] 构建完成！共生成 6538 条纯净事务记录。
[构建 训练集 Failed 事务集]

[构建器] 开始基于全量数据构建 Transaction 事务集...
构建事务: 100%|██████████| 3701/3701 [00:00<00:00, 56908.56row/s]
[构建器] 构建完成！共生成 3611 条纯净事务记录。

--- [Phase 4: 训练集对比模式挖掘] ---

[挖掘机] 启动全量数据关联规则挖掘...
[挖掘机] 正在执行前置项集频率剪枝...
[挖掘机] 剪枝完成！有效词表大小从 3461 缩减至 315
[挖掘机] 有效事务数从 6538 缩减至 4258
[挖掘机] 正在构建轻量级稀疏矩阵...(这会花点时间)
[挖掘机] 正在构建 FP-Tree...(这会花点时间)
[性能展示] FP-Growth 核心耗时: 0.0505 秒
[挖掘机] 成功挖掘出 11723 个频繁项集。
[挖掘机] 正在生成关联规则...(这会花点时间)
[性能展示] 事务映射 + 挖掘全流程总耗时: 10.1343 秒

[挖掘机] 正在基于训练集计算对比指标 (Growth Rate)...

🏆 Top 10 高特异性关联规则 (源自训练集):
   前件: [TARGET_Angiotensin-converting_enzyme] -> 后件: 【Hypertensive disease】
       (Support: 0.0031, Confidence: 0.5909, Lift: 43.38, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Gag-Pol_polyprotein] -> 后件: 【HIV Infections】
       (Support: 0.0066, Confidence: 0.7179, Lift: 109.18, GrowthRate: 23.75)
   前件: [TARGET_Reverse_transcriptase/RNaseH] -> 后件: 【HIV Infections】, [TARGET_Gag-Pol_polyprotein]
       (Support: 0.0038, Confidence: 0.8000, Lift: 121.66, GrowthRate: 13.57)
   前件: [TARGET_Reverse_transcriptase/RNaseH] -> 后件: 【HIV Infections】
       (Support: 0.0038, Confidence: 0.8000, Lift: 121.66, GrowthRate: 13.57)
   前件: [TARGET_Reverse_transcriptase/RNaseH], [TARGET_Gag-Pol_polyprotein] -> 后件: 【HIV Infections】
       (Support: 0.0038, Confidence: 0.8000, Lift: 121.66, GrowthRate: 13.57)
   前件: [TARGET_Gag-Pol_polyprotein] -> 后件: 【HIV Infections】, [TARGET_Reverse_transcriptase/RNaseH]
       (Support: 0.0038, Confidence: 0.4103, Lift: 109.18, GrowthRate: 13.57)
   前件: [TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-1] -> 后件: 【Sleeplessness】
       (Support: 0.0031, Confidence: 0.2131, Lift: 39.45, GrowthRate: 11.02)
   前件: [TARGET_Prostaglandin_G/H_synthase_1] -> 后件: [TARGET_Prostaglandin_G/H_synthase_2], 【Degenerative polyarthritis】
       (Support: 0.0061, Confidence: 0.1512, Lift: 22.99, GrowthRate: 4.41)
   前件: [TARGET_Prostaglandin_G/H_synthase_1], [TARGET_Prostaglandin_G/H_synthase_2] -> 后件: 【Degenerative polyarthritis】
       (Support: 0.0061, Confidence: 0.1576, Lift: 21.64, GrowthRate: 4.41)
   前件: [TARGET_Prostaglandin_G/H_synthase_1] -> 后件: 【Degenerative polyarthritis】
       (Support: 0.0061, Confidence: 0.1512, Lift: 20.76, GrowthRate: 4.41)

--- [Phase 5: 零样本药物重定位与双重验证 (Knowledge Discovery)] ---
🚀 系统分析完成！共发现 353 条潜在药物重定位关联！
   📊 统计验证：成功命中 20% 盲测集真实临床数据: 20 条
   🔭 科学探索：挖掘出超出已知数据库的全新潜在靶向组合: 333 条

🌟 Top 15 新药重定位候选推荐 (按置信度排序 - 反应治愈概率):
   💊 药物: Racivir -> 🎯 预测主治: HIV Infections  [🌟 零样本全新发现]
      (靶向机制: TARGET_Reverse_transcriptase/RNaseH
       关联基因: 间接机制 | 置信度: 0.8000 | 特异性: 13.57)
   💊 药物: 5-[(5-fluoro-3-methyl-1H-indazol-4-yl)oxy]benzene-1,3-dicarbonitrile -> 🎯 预测主治: HIV Infections  [🌟 零样本全新发现]
      (靶向机制: TARGET_Reverse_transcriptase/RNaseH
       关联基因: 间接机制 | 置信度: 0.8000 | 特异性: 13.57)
   💊 药物: Sennosides -> 🎯 预测主治: HIV Infections  [🌟 零样本全新发现]
      (靶向机制: TARGET_Reverse_transcriptase/RNaseH
       关联基因: AQP3 | 置信度: 0.8000 | 特异性: 13.57)
   💊 药物: Dexelvucitabine -> 🎯 预测主治: HIV Infections  [🌟 零样本全新发现]
      (靶向机制: TARGET_Reverse_transcriptase/RNaseH
       关联基因: 间接机制 | 置信度: 0.8000 | 特异性: 13.57)
   💊 药物: Tl-3-093 -> 🎯 预测主治: HIV Infections  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 间接机制 | 置信度: 0.7179 | 特异性: 23.75)
   💊 药物: N,N-[2,5-O-Dibenzyl-glucaryl]-DI-[1-amino-indan-2-OL] -> 🎯 预测主治: HIV Infections  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 间接机制 | 置信度: 0.7179 | 特异性: 23.75)
   💊 药物: (3S)-Tetrahydro-3-furanyl {(2S,3S)-4-[(2S,4R)-4-{(1S,2R)-2-[(S)-amino(hydroxy)methoxy]-2,3-dihydro-1H-inden-1-yl}-2-benzyl-3-oxo-2-pyrrolidinyl]-3-hydroxy-1-phenyl-2-butanyl}carbamate -> 🎯 预测主治: HIV Infections  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 间接机制 | 置信度: 0.7179 | 特异性: 23.75)
   💊 药物: (4R,5S,6S,7R)-1,3-dibenzyl-4,7-bis(phenoxymethyl)-5,6-dihydroxy-1,3 diazepan-2-one -> 🎯 预测主治: HIV Infections  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 间接机制 | 置信度: 0.7179 | 特异性: 23.75)
   💊 药物: N-[2-hydroxy-1-indanyl]-5-[(2-tertiarybutylaminocarbonyl)-4(benzo[1,3]dioxol-5-ylmethyl)-piperazino]-4-hydroxy-2-(1-phenylethyl)-pentanamide -> 🎯 预测主治: HIV Infections  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 间接机制 | 置信度: 0.7179 | 特异性: 23.75)
   💊 药物: (3,4-Dihydroxy-Phenyl)-Triphenyl-Arsonium -> 🎯 预测主治: HIV Infections  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 间接机制 | 置信度: 0.7179 | 特异性: 23.75)
   💊 药物: N-(3-Cyclopropyl(5,6,7,8,9,10-Hexahydro-2-Oxo-2h-Cycloocta[B]Pyran-3-Yl)Methyl)Phenylbenzensulfonamide -> 🎯 预测主治: HIV Infections  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 间接机制 | 置信度: 0.7179 | 特异性: 23.75)
   💊 药物: L-756423 -> 🎯 预测主治: HIV Infections  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 间接机制 | 置信度: 0.7179 | 特异性: 23.75)
   💊 药物: Zidovudine -> 🎯 预测主治: HIV Infections  [✅ 验证集完美命中]
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: FLT3, TERT | 置信度: 0.7179 | 特异性: 23.75)
   💊 药物: Didanosine -> 🎯 预测主治: HIV Infections  [✅ 验证集完美命中]
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: PNP | 置信度: 0.7179 | 特异性: 23.75)
   💊 药物: Fosamprenavir -> 🎯 预测主治: HIV Infections  [✅ 验证集完美命中]
      (靶向机制: TARGET_Gag-Pol_polyprotein
       关联基因: 间接机制 | 置信度: 0.7179 | 特异性: 23.75)

🔥 Top 15 新药重定位候选推荐 (按特异性/增长率排序 - 反应靶向独特性):
   💊 药物: Ramipril -> 🎯 预测主治: Hypertensive disease  [✅ 验证集完美命中]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)
   💊 药物: Trandolapril -> 🎯 预测主治: Hypertensive disease  [✅ 验证集完美命中]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)
   💊 药物: Benazepril -> 🎯 预测主治: Hypertensive disease  [✅ 验证集完美命中]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)
   💊 药物: Candoxatril -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)
   💊 药物: Perindopril -> 🎯 预测主治: Hypertensive disease  [✅ 验证集完美命中]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)
   💊 药物: Omapatrilat -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)
   💊 药物: Deserpidine -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)
   💊 药物: Rescinnamine -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)
   💊 药物: Cilazapril -> 🎯 预测主治: Hypertensive disease  [✅ 验证集完美命中]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)
   💊 药物: Epicaptopril -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)
   💊 药物: N-acetyl-alpha-D-glucosamine -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)
   💊 药物: beta-D-Ribopyranose -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)
   💊 药物: Ilepatril -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)
   💊 药物: Temocapril -> 🎯 预测主治: Hypertensive disease  [✅ 验证集完美命中]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)
   💊 药物: Isoquercetin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 0.5909 | 特异性: ∞)

🌈 更多长尾/多样的重定位候选:
   💊 药物: Isoflurane -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-1
       关联基因: 间接机制 | 置信度: 0.2131 | 特异性: 11.02)
   💊 药物: Dipyrithione -> 🎯 预测主治: Degenerative polyarthritis  [🌟 零样本全新发现]
      (靶向机制: TARGET_Prostaglandin_G/H_synthase_2
       关联基因: 间接机制 | 置信度: 0.1573 | 特异性: 3.96)

✅ 包含模型盲测验证标签的重定位清单已保存至: HFPM-DDA\output\new_drug_discoveries.csv

✅ 全流程执行完毕！
```
