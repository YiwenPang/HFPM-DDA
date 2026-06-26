# **HFPM-DDA**：**H**eterogeneous **F**requent **P**attern **M**ining for **D**rug-**D**isease **A**ssociation (基于异构频繁模式挖掘的药物-疾病关联网络)

这是一份大数据分析与挖掘课程的作业，利用关联规则算法，实现了**高特异性关联规则发现**，**新药重定位候选推荐**,也提供了**更多长尾/多样的重定位候选**.

![HFPM-DDA流程图](HFPM-DDA_Pipeline.jpg)

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
├── 📁 figures/                              # 论文插图
│   ├── 🪪 图1.svg                           # 事务化映射流程图
│   ├── 🪪 图1.vsdx                          # 事务化映射流程图
│   ├── 🪪 图2.svg                           # FP-Growth算法工作描述图
│   ├── 🪪 图2.vsdx                          # FP-Growth算法工作描述图
│   ├── 🪪 图3.svg                           # 模型整体流程图
│   └── 🪪 图3.vsdx                          # 模型整体流程图
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

原始模型版

```text
C:\Users\*****\miniconda3\envs\hfpm-dda\python.exe C:\Users\*****\PycharmProjects\HFPM-DDA\source\main.py 
============================================================
🚀 欢迎启动 HFPM-DDA 关联规则深度挖掘与新药发现系统 🚀
============================================================

--- [Phase 1: 异构数据流式加载] ---
[解析器] 开始流式解析 DrugBank XML 寻找靶点与基因特征... (这会花点时间)
正在解析 DrugBank 药物: 3963135 drugs [00:39, 101308.99 drugs/s]
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
构建事务: 100%|██████████| 7144/7144 [00:00<00:00, 31461.25row/s]
[构建器] 构建完成！共生成 6538 条纯净事务记录。
[构建 训练集 Failed 事务集]

[构建器] 开始基于全量数据构建 Transaction 事务集...
构建事务: 100%|██████████| 3701/3701 [00:00<00:00, 29270.62row/s]
[构建器] 构建完成！共生成 3611 条纯净事务记录。

--- [Phase 4: 训练集对比模式挖掘] ---

[挖掘机] 启动全量数据关联规则挖掘...
[挖掘机] 正在执行前置项集频率剪枝...
[挖掘机] 剪枝完成！有效词表大小从 3461 缩减至 314
[挖掘机] 有效事务数从 6538 缩减至 1909
[挖掘机] 正在构建轻量级稀疏矩阵...(这会花点时间)
[挖掘机] 正在构建 FP-Tree...(这会花点时间)
[性能展示] FP-Growth 核心耗时: 0.0356 秒
[挖掘机] 成功挖掘出 9181 个频繁项集。
[挖掘机] 正在生成关联规则...(这会花点时间)
[性能展示] 事务映射 + 挖掘全流程总耗时: 8.5565 秒

[挖掘机] 正在基于训练集计算对比指标 (Growth Rate)...

--- [Phase 4.5: 规则精炼与去冗余] ---
🧹 [去冗余] 成功抹除 174 条同质化超集规则，保留最纯粹特征组合。

🥇 各疾病高分代表机制 (Disease Representative Mechanisms):
   🎯 疾病: 【Hypertensive disease】
       => 核心靶向机制: [TARGET_Angiotensin-converting_enzyme]
       => [Score: 272.5 | Conf: 1.0000 | Supp: 0.0068 | GR: ∞]
   🎯 疾病: 【Sleeplessness】
       => 核心靶向机制: [TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-5]
       => [Score: 269.4 | Conf: 1.0000 | Supp: 0.0052 | GR: ∞]
   🎯 疾病: 【Peptic Ulcer】
       => 核心靶向机制: [TARGET_Potassium-transporting_ATPase_alpha_chain_1]
       => [Score: 266.2 | Conf: 1.0000 | Supp: 0.0037 | GR: ∞]
   🎯 疾病: 【Hot flushes】
       => 核心靶向机制: [TARGET_Mineralocorticoid_receptor], [TARGET_Estrogen_receptor]
       => [Score: 240.2 | Conf: 0.7500 | Supp: 0.0031 | GR: ∞]
   🎯 疾病: 【HIV Infections】
       => 核心靶向机制: [TARGET_Gag-Pol_polyprotein]
       => [Score: 220.1 | Conf: 0.8485 | Supp: 0.0147 | GR: 52.96]
   🎯 疾病: 【Tinea corporis (disorder)】
       => 核心靶向机制: [TARGET_Lanosterol_14-alpha_demethylase]
       => [Score: 205.2 | Conf: 0.4000 | Supp: 0.0031 | GR: ∞]
   🎯 疾病: 【Osteoporosis, Postmenopausal】
       => 核心靶向机制: [TARGET_Estrogen_receptor]
       => [Score: 188.1 | Conf: 0.2188 | Supp: 0.0037 | GR: ∞]
   🎯 疾病: 【Acne Vulgaris】
       => 核心靶向机制: [TARGET_Androgen_receptor]
       => [Score: 186.6 | Conf: 0.2143 | Supp: 0.0031 | GR: ∞]
   🎯 疾病: 【Schizophrenia】
       => 核心靶向机制: [TARGET_Calmodulin], [TARGET_D(2)_dopamine_receptor]
       => [Score: 80.5 | Conf: 0.6667 | Supp: 0.0031 | GR: 3.78]
   🎯 疾病: 【Tinea Pedis】
       => 核心靶向机制: [TARGET_Lanosterol_14-alpha_demethylase]
       => [Score: 80.5 | Conf: 0.4667 | Supp: 0.0037 | GR: 13.24]

🏆 Top 10 高特异性关联规则 (多样性筛选):
   前件: [TARGET_Potassium-transporting_ATPase_alpha_chain_1] -> 后件: 【Peptic Ulcer】
       (Support: 0.0037, Confidence: 1.0000, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Glutamate_receptor_2] -> 后件: 【Sleeplessness】
       (Support: 0.0042, Confidence: 1.0000, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4] -> 后件: 【Sleeplessness】
       (Support: 0.0042, Confidence: 1.0000, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Mineralocorticoid_receptor], [TARGET_Estrogen_receptor] -> 后件: 【Hot flushes】
       (Support: 0.0031, Confidence: 0.7500, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Mineralocorticoid_receptor], [TARGET_Androgen_receptor] -> 后件: 【Hot flushes】
       (Support: 0.0037, Confidence: 0.7000, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Lanosterol_14-alpha_demethylase] -> 后件: 【Tinea corporis (disorder)】
       (Support: 0.0031, Confidence: 0.4000, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Voltage-dependent_L-type_calcium_channel_subunit_alpha-1C] -> 后件: 【Hypertensive disease】
       (Support: 0.0052, Confidence: 1.0000, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Angiotensin-converting_enzyme] -> 后件: 【Hypertensive disease】
       (Support: 0.0068, Confidence: 1.0000, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Estrogen_receptor] -> 后件: 【Osteoporosis, Postmenopausal】
       (Support: 0.0037, Confidence: 0.2188, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Muscarinic_acetylcholine_receptor_M3], [TARGET_Muscarinic_acetylcholine_receptor_M5] -> 后件: 【Peptic Ulcer】
       (Support: 0.0052, Confidence: 0.2174, GrowthRate: ∞ (纯正向))

--- [Phase 5: 零样本药物重定位与双重验证] ---
🚀 系统分析完成！共发现 2073 条潜在药物重定位关联！
   📊 统计验证：成功命中 20% 盲测集真实临床数据: 55 条
   🔭 科学探索：挖掘出超出已知数据库的全新潜在靶向组合: 2018 条

🌟 Top 15 新药重定位候选推荐 (按置信度排序 - 反应治愈概率):
   💊 药物: Mirogabalin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Atagabalin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Imagabalin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Z-160 -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: N-acetyl-alpha-D-glucosamine -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: beta-D-Ribopyranose -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Ilepatril -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Temocapril -> 🎯 预测主治: Hypertensive disease  [✅ 验证集完美命中]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Isoquercetin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Gallopamil -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Zofenopril -> 🎯 预测主治: Hypertensive disease  [✅ 验证集完美命中]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Acetate -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Idrapril -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Utibapril -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Alacepril -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)

🔥 Top 15 新药重定位候选推荐 (按特异性/增长率排序 - 反应靶向独特性):
   💊 药物: Mirogabalin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Atagabalin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Imagabalin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Z-160 -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: N-acetyl-alpha-D-glucosamine -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: beta-D-Ribopyranose -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Ilepatril -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Temocapril -> 🎯 预测主治: Hypertensive disease  [✅ 验证集完美命中]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Isoquercetin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Gallopamil -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Zofenopril -> 🎯 预测主治: Hypertensive disease  [✅ 验证集完美命中]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Acetate -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Idrapril -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Utibapril -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Alacepril -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Angiotensin-converting_enzyme
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)

🌈 更多长尾/多样的重定位候选:
   💊 药物: 5-[(5-fluoro-3-methyl-1H-indazol-4-yl)oxy]benzene-1,3-dicarbonitrile -> 🎯 预测主治: HIV Infections  [🌟 零样本全新发现]
      (靶向机制: TARGET_Reverse_transcriptase/RNaseH
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: 30.27)
   💊 药物: Panadiplon -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: 24.59)
   💊 药物: Linaprazan -> 🎯 预测主治: Peptic Ulcer  [🌟 零样本全新发现]
      (靶向机制: TARGET_Potassium-transporting_ATPase_alpha_chain_1
       关联基因: ATP4A | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Promethazine -> 🎯 预测主治: Schizophrenia  [🌟 零样本全新发现]
      (靶向机制: TARGET_Calmodulin, TARGET_D(2)_dopamine_receptor
       关联基因: KCNH4, KCNH1, KCNG3, P2RY8, P2RY12, KCNQ4, KCND3, SCN11A, P2RX4, KCNH6, P2RY14, ADRA1A, KCNV1, SCN1A, CALM3, KCNA1, HRH2, KCNC1, GRIN2A, GRIN3B, KCNA10, KCNC4, KCNA4, KCNH2, P2RY13, SCN7A, SCN2A, SCN3A, GRIN3A, CHRM4, P2RY1, P2RX7, P2RY10, KCNAB1, P2RY4, KCNG1, KCNQ3, KCNS1, KCNQ2, GRIN2D, KCNE1, KCNE2, SCN8A, KCNB1, KCNH3, P2RX3, CALM1, KCNH7, KCNE4, KCNC3, GRIN1, ADRA1B, KCNE5, KCNB2, ADRA2B, KCNC2, P2RX5, ADRA2C, GRIN2B, KCND2, KCNA3, KCNA5, P2RX1, DRD2, P2RY2, KCNQ1, KCNA2, SCN10A, CHRM5, KCNF1, P2RY11, ADRA2A, CHRM3, KCNV2, P2RX6, SCN9A, KCNG4, GRIN2C, CHRM2, KCNH5, LPAR4, KCNS3, CHRM1, KCNG2, P2RX2, KCNH8, HRH1, CALM2, KCNA6, KCNQ5, KCNE3, ADRA1D, KCND1, SCN4A, SCN5A, KCNAB2, LPAR6 | 置信度: 0.6667 | 特异性: 3.78)
   💊 药物: 4-(6-HYDROXY-BENZO[D]ISOXAZOL-3-YL)BENZENE-1,3-DIOL -> 🎯 预测主治: Hot flushes  [🌟 零样本全新发现]
      (靶向机制: TARGET_Estrogen_receptor_beta
       关联基因: 间接机制 | 置信度: 0.5385 | 特异性: ∞)
   💊 药物: Flutrimazole -> 🎯 预测主治: Tinea Pedis  [🌟 零样本全新发现]
      (靶向机制: TARGET_Lanosterol_14-alpha_demethylase
       关联基因: 间接机制 | 置信度: 0.4667 | 特异性: 13.24)
   💊 药物: Isavuconazole -> 🎯 预测主治: Tinea corporis (disorder)  [🌟 零样本全新发现]
      (靶向机制: TARGET_Lanosterol_14-alpha_demethylase
       关联基因: 间接机制 | 置信度: 0.4000 | 特异性: ∞)
   💊 药物: Tigemocoxib -> 🎯 预测主治: Degenerative polyarthritis  [🌟 零样本全新发现]
      (靶向机制: TARGET_Prostaglandin_G/H_synthase_2
       关联基因: 间接机制 | 置信度: 0.3182 | 特异性: 8.83)
   💊 药物: Icosapent -> 🎯 预测主治: Diabetes Mellitus, Non-Insulin-Dependent  [🌟 零样本全新发现]
      (靶向机制: TARGET_Peroxisome_proliferator-activated_receptor_gamma
       关联基因: 间接机制 | 置信度: 0.3158 | 特异性: 11.35)
   💊 药物: Amineptine -> 🎯 预测主治: Major Depressive Disorder  [🌟 零样本全新发现]
      (靶向机制: TARGET_Sodium-dependent_serotonin_transporter
       关联基因: SLC6A4, SLC6A3, SLC6A2 | 置信度: 0.2791 | 特异性: 3.78)
   💊 药物: Darbufelone -> 🎯 预测主治: Rheumatoid Arthritis  [🌟 零样本全新发现]
      (靶向机制: TARGET_Prostaglandin_G/H_synthase_2
       关联基因: 间接机制 | 置信度: 0.2727 | 特异性: 9.08)
   💊 药物: Tebufelone -> 🎯 预测主治: Pain  [🌟 零样本全新发现]
      (靶向机制: TARGET_Prostaglandin_G/H_synthase_1
       关联基因: ALOX5, PTGS2, PTGS1 | 置信度: 0.2262 | 特异性: 3.99)
   💊 药物: (9BETA,11ALPHA,13ALPHA,14BETA,17ALPHA)-11-(METHOXYMETHYL)ESTRA-1(10),2,4-TRIENE-3,17-DIOL -> 🎯 预测主治: Osteoporosis, Postmenopausal  [🌟 零样本全新发现]
      (靶向机制: TARGET_Estrogen_receptor
       关联基因: ESR1, NCOA2 | 置信度: 0.2188 | 特异性: ∞)
   💊 药物: Mitotane -> 🎯 预测主治: Acne Vulgaris  [🌟 零样本全新发现]
      (靶向机制: TARGET_Androgen_receptor
       关联基因: FDX1, ESR1, PGR, CYP11B1, AR | 置信度: 0.2143 | 特异性: ∞)
   💊 药物: Alprenolol -> 🎯 预测主治: Glaucoma, Open-Angle  [🌟 零样本全新发现]
      (靶向机制: TARGET_Beta-1_adrenergic_receptor
       关联基因: ADRB3, ADRB2, HTR1A, ADRB1 | 置信度: 0.1556 | 特异性: 13.24)

✅ 包含模型盲测验证标签的重定位清单已保存至: C:\Users\*****\PycharmProjects\HFPM-DDA\output\new_drug_discoveries.csv

✅ 全流程执行完毕！

进程已结束，退出代码为 0
```
Spark 版
```text
C:\Users\*****\miniconda3\envs\hfpm-dda\python.exe C:\Users\*****\PycharmProjects\HFPM-DDA\source\spark_main.py 
============================================================
🚀 欢迎启动 HFPM-DDA (PySpark 大数据分布式重构版) 🚀
============================================================

--- [Phase 1: 异构数据解析 (Driver 端)] ---
[解析器] 开始流式解析 DrugBank XML 寻找靶点与基因特征... (这会花点时间)
正在解析 DrugBank 药物: 3963135 drugs [00:40, 98233.45 drugs/s]
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

--- [Phase 2: 加载全量临床数据 & 严格对齐切分 (Driver 端)] ---
[数据] 成功(Approved)记录: 8931 条
[数据] 失败(Terminated/Withdrawn等)记录: 4627 条

--- [Phase 2.5: 本地写盘 & 转换为 Spark DataFrame] ---
[Spark划分] 训练集(Approved): 7144 条已写入硬盘 | 测试集(Approved): 1787 条已写入硬盘

--- [Phase 3: 分布式事务映射构建与严格剪枝 (UDF)] ---
[构建器] 构建完成！剪枝后有效训练集事务(Approved): 6538 条

--- [Phase 4: 训练集对比模式挖掘 (Spark MLlib)] ---

[剪枝] 正在执行前置项集频率剪枝...
[剪枝] 有效词表大小从 3461 缩减至 314
[剪枝] 有效事务数从 6538 缩减至 1909

[Spark挖掘机] 启动分布式关联规则挖掘 (基于 PySpark MLlib)...
[Spark挖掘机] 正在构建分布式 FP-Tree 并挖掘频繁项集...(交由 Spark 引擎计算)
[性能展示] Spark MLlib 分布式计算核心耗时: 0.4889 秒
[Spark挖掘机] 正在将严格过滤后的规则映射回 Pandas 格式...
                                                                                
[分析器] 正在拉取失败集到本地计算对比指标 (Growth Rate)...

--- [Phase 4.5: Spark分布式结果精炼与去冗余] ---
🧹 [去冗余] 成功抹除 1023 条同质化超集规则。

🥇 Spark挖掘各疾病高分代表机制:
   🎯 疾病: 【Hypertensive disease】
       => 核心靶向机制: [TARGET_Angiotensin-converting_enzyme]
       => [Score: 272.5 | Conf: 1.0000 | Supp: 0.0068 | GR: ∞]
   🎯 疾病: 【Sleeplessness】
       => 核心靶向机制: [TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-5]
       => [Score: 269.4 | Conf: 1.0000 | Supp: 0.0052 | GR: ∞]
   🎯 疾病: 【Peptic Ulcer】
       => 核心靶向机制: [TARGET_Potassium-transporting_ATPase_alpha_chain_1]
       => [Score: 266.2 | Conf: 1.0000 | Supp: 0.0037 | GR: ∞]
   🎯 疾病: 【Hot flushes】
       => 核心靶向机制: [TARGET_Mineralocorticoid_receptor], [TARGET_Estrogen_receptor]
       => [Score: 240.2 | Conf: 0.7500 | Supp: 0.0031 | GR: ∞]
   🎯 疾病: 【HIV Infections】
       => 核心靶向机制: [TARGET_Gag-Pol_polyprotein]
       => [Score: 220.1 | Conf: 0.8485 | Supp: 0.0147 | GR: 52.96]
   🎯 疾病: 【Tinea corporis (disorder)】
       => 核心靶向机制: [TARGET_Lanosterol_14-alpha_demethylase]
       => [Score: 205.2 | Conf: 0.4000 | Supp: 0.0031 | GR: ∞]
   🎯 疾病: 【Osteoporosis, Postmenopausal】
       => 核心靶向机制: [TARGET_Estrogen_receptor]
       => [Score: 188.1 | Conf: 0.2188 | Supp: 0.0037 | GR: ∞]
   🎯 疾病: 【Acne Vulgaris】
       => 核心靶向机制: [TARGET_Androgen_receptor]
       => [Score: 186.6 | Conf: 0.2143 | Supp: 0.0031 | GR: ∞]
   🎯 疾病: 【Schizophrenia】
       => 核心靶向机制: [TARGET_Calmodulin], [TARGET_D(2)_dopamine_receptor]
       => [Score: 80.5 | Conf: 0.6667 | Supp: 0.0031 | GR: 3.78]
   🎯 疾病: 【Tinea Pedis】
       => 核心靶向机制: [TARGET_Lanosterol_14-alpha_demethylase]
       => [Score: 80.5 | Conf: 0.4667 | Supp: 0.0037 | GR: 13.24]

🏆 Top 10 高特异性关联规则 (基于 Spark 分布式挖掘, 多样性筛选):
   前件: [TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4] -> 后件: 【Sleeplessness】
       (Support: 0.0042, Confidence: 1.0000, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Glutamate_receptor_ionotropic,_kainate_2] -> 后件: 【Sleeplessness】
       (Support: 0.0042, Confidence: 1.0000, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Potassium-transporting_ATPase_alpha_chain_1] -> 后件: 【Peptic Ulcer】
       (Support: 0.0037, Confidence: 1.0000, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Mineralocorticoid_receptor], [TARGET_Estrogen_receptor] -> 后件: 【Hot flushes】
       (Support: 0.0031, Confidence: 0.7500, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Androgen_receptor], [TARGET_Mineralocorticoid_receptor] -> 后件: 【Hot flushes】
       (Support: 0.0037, Confidence: 0.7000, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Lanosterol_14-alpha_demethylase] -> 后件: 【Tinea corporis (disorder)】
       (Support: 0.0031, Confidence: 0.4000, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1] -> 后件: 【Hypertensive disease】
       (Support: 0.0031, Confidence: 1.0000, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Angiotensin-converting_enzyme] -> 后件: 【Hypertensive disease】
       (Support: 0.0068, Confidence: 1.0000, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Estrogen_receptor] -> 后件: 【Osteoporosis, Postmenopausal】
       (Support: 0.0037, Confidence: 0.2188, GrowthRate: ∞ (纯正向))
   前件: [TARGET_Muscarinic_acetylcholine_receptor_M5], [TARGET_Muscarinic_acetylcholine_receptor_M3] -> 后件: 【Peptic Ulcer】
       (Support: 0.0052, Confidence: 0.2174, GrowthRate: ∞ (纯正向))

--- [Phase 5: 零样本药物重定位与双重验证] ---

🚀 Spark 分析完成！共发现 2073 条潜在药物重定位关联！
   📊 统计验证：成功命中 20% 盲测集真实临床数据: 55 条
   🔭 科学探索：挖掘出超出已知数据库的全新潜在靶向组合: 2018 条

🌟 Top 15 新药重定位候选推荐 (按置信度排序 - 反应治愈概率):
   💊 药物: Methylphenobarbital -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Glutamic acid -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Glutamate_receptor_ionotropic,_kainate_2
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Ethanol -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Butalbital -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Meprobamate -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Thiopental -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Heptabarbital -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Hexobarbital -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Dihydro-2-thioxo-5-((5-(2-(trifluoromethyl)phenyl)-2-furanyl)methyl)-4,6(1H,5H)-pyrimidinedione -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Primidone -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Imagabalin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Atagabalin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Mirogabalin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Gabapentin enacarbil -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Nilvadipine -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)

🔥 Top 15 新药重定位候选推荐 (按特异性/增长率排序 - 反应靶向独特性):
   💊 药物: Methylphenobarbital -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Glutamic acid -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Glutamate_receptor_ionotropic,_kainate_2
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Ethanol -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Butalbital -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Meprobamate -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Thiopental -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Heptabarbital -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Hexobarbital -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Dihydro-2-thioxo-5-((5-(2-(trifluoromethyl)phenyl)-2-furanyl)methyl)-4,6(1H,5H)-pyrimidinedione -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Primidone -> 🎯 预测主治: Sleeplessness  [🌟 零样本全新发现]
      (靶向机制: TARGET_Gamma-aminobutyric_acid_receptor_subunit_alpha-4
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Imagabalin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Atagabalin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Mirogabalin -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Gabapentin enacarbil -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Nilvadipine -> 🎯 预测主治: Hypertensive disease  [🌟 零样本全新发现]
      (靶向机制: TARGET_Voltage-dependent_calcium_channel_subunit_alpha-2/delta-1
       关联基因: 间接机制 | 置信度: 1.0000 | 特异性: ∞)

🌈 更多长尾/多样的重定位候选:
   💊 药物: Sennosides -> 🎯 预测主治: HIV Infections  [🌟 零样本全新发现]
      (靶向机制: TARGET_Reverse_transcriptase/RNaseH
       关联基因: AQP3 | 置信度: 1.0000 | 特异性: 30.27)
   💊 药物: Pumaprazole -> 🎯 预测主治: Peptic Ulcer  [🌟 零样本全新发现]
      (靶向机制: TARGET_Potassium-transporting_ATPase_alpha_chain_1
       关联基因: ATP4A | 置信度: 1.0000 | 特异性: ∞)
   💊 药物: Promethazine -> 🎯 预测主治: Schizophrenia  [🌟 零样本全新发现]
      (靶向机制: TARGET_Calmodulin, TARGET_D(2)_dopamine_receptor
       关联基因: KCNA5, KCNH5, P2RX2, GRIN2C, KCNQ5, SCN4A, P2RX1, KCNS1, GRIN2A, KCNQ4, KCNQ2, KCNA4, KCNC3, KCNF1, P2RX4, KCNAB2, P2RY4, KCNC2, KCND1, DRD2, KCNH7, KCNQ3, KCNG2, KCNH6, P2RY11, ADRA2A, LPAR6, P2RY1, GRIN3B, GRIN1, KCNV1, SCN11A, KCNH3, KCNG1, SCN8A, KCNE5, KCNS3, KCNE3, SCN5A, GRIN3A, P2RY12, KCNC4, CHRM4, KCNB2, CALM1, ADRA2C, P2RY8, CHRM3, ADRA1B, KCNE2, KCNH2, CALM2, P2RX3, KCNA10, CHRM5, SCN2A, CHRM2, KCNAB1, ADRA1A, ADRA2B, KCNC1, KCND2, KCNA6, KCNA2, KCNE4, P2RY10, KCNE1, KCNB1, KCND3, KCNV2, SCN1A, KCNA1, ADRA1D, LPAR4, SCN7A, KCNQ1, KCNH1, P2RY13, CHRM1, P2RY2, SCN3A, KCNA3, P2RX5, HRH1, SCN9A, P2RX7, KCNG3, GRIN2D, P2RY14, KCNH8, CALM3, HRH2, KCNH4, KCNG4, P2RX6, SCN10A, GRIN2B | 置信度: 0.6667 | 特异性: 3.78)
   💊 药物: 5-HYDROXY-2-(4-HYDROXYPHENYL)-1-BENZOFURAN-7-CARBONITRILE -> 🎯 预测主治: Hot flushes  [🌟 零样本全新发现]
      (靶向机制: TARGET_Estrogen_receptor_beta
       关联基因: 间接机制 | 置信度: 0.5385 | 特异性: ∞)
   💊 药物: Azalanstat -> 🎯 预测主治: Tinea Pedis  [🌟 零样本全新发现]
      (靶向机制: TARGET_Lanosterol_14-alpha_demethylase
       关联基因: 间接机制 | 置信度: 0.4667 | 特异性: 13.24)
   💊 药物: Fluconazole -> 🎯 预测主治: Tinea corporis (disorder)  [🌟 零样本全新发现]
      (靶向机制: TARGET_Lanosterol_14-alpha_demethylase
       关联基因: 间接机制 | 置信度: 0.4000 | 特异性: ∞)
   💊 药物: Tigemocoxib -> 🎯 预测主治: Degenerative polyarthritis  [🌟 零样本全新发现]
      (靶向机制: TARGET_Prostaglandin_G/H_synthase_2
       关联基因: 间接机制 | 置信度: 0.3182 | 特异性: 8.83)
   💊 药物: Leriglitazone -> 🎯 预测主治: Diabetes Mellitus, Non-Insulin-Dependent  [🌟 零样本全新发现]
      (靶向机制: TARGET_Peroxisome_proliferator-activated_receptor_gamma
       关联基因: 间接机制 | 置信度: 0.3158 | 特异性: 11.35)
   💊 药物: Atomoxetine -> 🎯 预测主治: Major Depressive Disorder  [🌟 零样本全新发现]
      (靶向机制: TARGET_Sodium-dependent_serotonin_transporter
       关联基因: OPRK1, GRIN1, GRIN3A, GRIN2A, GRIN2C, SLC6A2, KCNJ3, SLC6A4, GRIN2D, GRIN2B, GRIN3B | 置信度: 0.2791 | 特异性: 3.78)
   💊 药物: Daleuton -> 🎯 预测主治: Rheumatoid Arthritis  [🌟 零样本全新发现]
      (靶向机制: TARGET_Prostaglandin_G/H_synthase_2
       关联基因: 间接机制 | 置信度: 0.2727 | 特异性: 9.08)
   💊 药物: Cannabidiol -> 🎯 预测主治: Pain  [🌟 零样本全新发现]
      (靶向机制: TARGET_Prostaglandin_G/H_synthase_1
       关联基因: HTR2A, NQO1, TRPM8, GLRA1, GPX1, TRPA1, TRPV3, PTGS1, CNR1, CACNA1H, GPR18, GPR55, VDAC1, HTR1A, IDO1, GPR12, HMGCR, CNR2, CHRNA7, ADORA1, TRPV1, PTGS2, CYP17A1, TRPV4, HTR3A, OPRM1, CACNA1I, NAAA, CACNA1G, PPARG, OPRD1, ACAT1, TRPV2, AANAT, GLRA3, GLRB, SOD1, GSR, CAT | 置信度: 0.2262 | 特异性: 3.99)
   💊 药物: Conjugated estrogens -> 🎯 预测主治: Osteoporosis, Postmenopausal  [🌟 零样本全新发现]
      (靶向机制: TARGET_Estrogen_receptor
       关联基因: ESR1, ESR2 | 置信度: 0.2188 | 特异性: ∞)
   💊 药物: Spironolactone -> 🎯 预测主治: Acne Vulgaris  [🌟 零样本全新发现]
      (靶向机制: TARGET_Androgen_receptor
       关联基因: CACNB3, CACNB4, ESR1, CACNA1C, ESR2, NR3C2, CACNA1D, CACNA1S, CACNB1, CACNA1A, CACNB2, NR1I2, AR, NR3C1, PGR | 置信度: 0.2143 | 特异性: ∞)
   💊 药物: Nadolol -> 🎯 预测主治: Glaucoma, Open-Angle  [🌟 零样本全新发现]
      (靶向机制: TARGET_Beta-1_adrenergic_receptor
       关联基因: ADRB2, ADRB1 | 置信度: 0.1556 | 特异性: 13.24)
✅ 包含 Spark 模型盲测验证标签的清单已保存至: C:\Users\*****\PycharmProjects\HFPM-DDA\output\spark_new_drug_discoveries.csv

✅ Spark 任务执行完毕，集群资源已释放！

进程已结束，退出代码为 0
```