# MGS 4701 W01 Fall 2026 — Track 5 试点数据集

**研究主题**：BA（商业分析）/ DS（数据科学）硕士项目招生面试 —— 面试考察什么？不同地区与项目类型有何差异？WKU 申请者应如何准备？

**受众**：WKU（温州肯恩大学）申请 BA/DS 硕士的同学（本人），时间规划 2026 年 10–12 月。

## 数据是什么

`data/pilot_dataset_cleaned.csv`：**100 条** BA/DS 硕士项目的招生面试信息，覆盖 6 个地区（美国 40、英国 18、中国香港 18、新加坡 13、澳大利亚 9、中国澳门 2）、80 所院校、47 个项目方向。

每条记录含：面试形式（8 类标准化编码）、面试平台、题目数量/时长、问题类型、典型面试问题示例、可验证来源 URL、来源类型。

## 数据来源与收集时间

- **来源**：院校招生官网（100% 记录含官网交叉验证）+ 中文面经社区（知乎、小红书、一亩三分地、新东方、指南者留学等）的公开面经帖。
- **收集时间**：2026 年 9 月 20–25 日，手动收集。
- **回退记录**：首选 Reddit r/gradadmissions 官方 API 因网络环境无法稳定访问，触发协议回退，改走「官网 + 中文面经社区」主路径；12 月正式轮计划补充 8–12 个 WKU 校友半结构化访谈。
- 收集与纳入/排除规则详见 `docs/collection_protocol.md`，字段编码规则详见 `docs/coding_scheme.md`。

## 如何复现

```bash
# 1. 原始收集表 → raw CSV（已导出为 data/pilot_dataset_raw.csv）
# 2. 清洗与标准化（面试形式 8 类编码、平台标签、题数/时长解析）
python scripts/01_clean_data.py

# 3. 探索性分析（图表与结论）
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/01_data_cleaning.ipynb
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/02_exploratory_analysis.ipynb
# 或直接在 Jupyter 中打开 notebooks/ 下的两个 notebook 运行
```

## 目录结构

```
MGS4701_Track5/
├── data/
│   ├── pilot_dataset_raw.csv        # 原始数据（11 列，100 条）
│   └── pilot_dataset_cleaned.csv    # 清洗后（16 列，含编码与解析字段）
├── notebooks/
│   ├── 01_data_cleaning.ipynb       # 清洗与标准化（含执行结果）
│   └── 02_exploratory_analysis.ipynb# EDA：地区×形式、平台、问题类型、时长（含图表）
├── scripts/
│   ├── 01_clean_data.py             # 清洗脚本（与 notebook 01 逻辑一致）
│   └── build_notebooks.py           # notebook 构建器（可重建两个 ipynb）
├── docs/
│   ├── coding_scheme.md             # 编码表（8 类面试形式定义、解析规则、QC）
│   └── collection_protocol.md       # 收集协议（抽样框、回退阶梯、复现路径、合规）
└── README.md
```

## 试点关键发现（摘要）

1. **面试普遍性**：94% 的方向有面试环节（或部分候选人面试）；仅 6 个方向明确无强制面试。
2. **形式差异**：美国/英国流行**异步录播视频（Kira Talent）**；中国香港/新加坡流行**真人视频 + 笔试/机考组合**（新加坡 39% 为笔试+真人面）。
3. **问题类型**：动机题（Why-this-program）与行为题覆盖最广；技术题（统计/概率/编程）集中在异步录播与技术向项目；AI 伦理/案例题开始出现。
4. **时长**：中位数约 17.5 分钟；美国部分项目（杜克 MQM、沃顿 MIS）明显更长（30–45 分钟）。
5. **对 WKU 申请者**：主攻真人视频 + 行为/动机题库；东亚项目补充数学/统计/编程笔试准备；Kira 类注意限时作答与写作题。

> 试点数据用于方法验证；正式推断需 12 月扩展至 ≥300 条并纳入访谈数据。
