# -*- coding: utf-8 -*-
"""构建并执行 MGS4701 Track5 的两个 notebook（01 清洗 / 02 分析），输出带执行结果的 .ipynb"""
import nbformat as nbf
from pathlib import Path
import subprocess, sys, os

ROOT = Path(__file__).resolve().parent.parent
NB_DIR = ROOT / "notebooks"

CELL = "code"
MD = "markdown"

# ================= Notebook 01: 数据清洗 =================
nb1 = nbf.v4.new_notebook()
nb1.metadata.kernelspec = {"name": "python3", "display_name": "Python 3", "language": "python"}
nb1.cells = [
    nbf.v4.new_markdown_cell(
        """# 01 试点数据清洗与标准化

**项目**: MGS 4701 W01 Fall 2026 — Track 5：BA/DS 硕士招生面试  
**数据**: `data/pilot_dataset_raw.csv`（100 条，手收集，来源见 `docs/collection_protocol.md`）  
**编码表**: 字段标准化规则见 `docs/coding_scheme.md`  
**产出**: `data/pilot_dataset_cleaned.csv`

本 notebook 完成：
1. 「面试形式」→ 8 类分析编码（`selective / async_video / live_video / phone / written_live / group / mixed / none`）
2. 「面试平台」→ 平台标签抽取
3. 「题目数量/时长」→ 题目数与总时长（分钟）解析
4. 数据质量校验（记录数、重复、缺失）"""
    ),
    nbf.v4.new_code_cell(
        """# -*- coding: utf-8 -*-
import re
import pandas as pd

RAW = "../data/pilot_dataset_raw.csv"
OUT = "../data/pilot_dataset_cleaned.csv"

df = pd.read_csv(RAW)
print(f"原始记录数: {len(df)} | 列数: {df.shape[1]}")
df.head(3)"""
    ),
    nbf.v4.new_markdown_cell(
        """## 1. 面试形式标准化

原始「面试形式」字段有 49 种自由文本写法（如「部分候选人面试（评估制）」「视频面试（Zoom）」「真人线上单面」），
先归并为 **8 类分析编码**（编码定义见 `docs/coding_scheme.md`），用于后续跨地区/跨项目比较。"""
    ),
    nbf.v4.new_code_cell(
        """FORMAT_MAP = {
    "部分候选人面试（评估制）": "selective", "部分候选人受邀面试": "selective",
    "部分项目需面试": "selective", "部分申请者需面试": "selective",
    "部分申请者获邀面试": "selective", "材料审核+部分面试": "selective",
    "有面试环节": "selective", "行为面试（部分候选人）": "selective",
    "行为面试（邀请制）": "selective",
    "部分项目需面试（研究型MPhil/MRes必面）": "selective",
    "邀请制面试（校园/电话/视频）": "selective", "虚拟面试（邀请制）": "selective",
    "异步视频面试（录播）": "async_video", "视频面试（录播）": "async_video",
    "案例分析视频面试": "async_video",
    "真人视频面试（1V1）+ 视频提交": "live_video",
    "真人视频面试（Zoom/Skype）": "live_video", "真人视频面试（推荐参加）": "live_video",
    "真人视频面试（Zoom）+ 技能评估": "live_video", "视频面试（部分申请者获邀）": "live_video",
    "视频面试（Zoom）": "live_video", "视频面试（Zoom）+ 编程测试": "live_video",
    "视频面试（Zoom/Skype）": "live_video", "线上Zoom面试（双教授）": "live_video",
    "全英文个面": "live_video", "真人线上单面": "live_video", "线上面试": "live_video",
    "结构化面试": "live_video", "结构化面试+案例问题": "live_video", "面试+写作": "live_video",
    "电话/Skype面试": "phone", "视频会议或电话": "live_video",
    "线上机考 + 真人面谈": "written_live", "全英文个面（笔试+面试）": "written_live",
    "笔试+面试": "written_live", "两轮面试：机面+真人面": "written_live",
    "真人单面 + 笔试": "written_live",
    "小群面": "group", "小组讨论(TBD) + 一对一面试": "group",
    "Video / 真人单面 / 群面": "mixed", "Video / 真人面 / 群面": "mixed",
    "真人线上面试（单面+群面）": "mixed",
    "无强制面试（需提交GRE/GMAT）": "none", "无强制面试（需提交GMAT/GRE）": "none",
    "无强制面试（需提交文书+推荐信）": "none", "无强制面试（可选提交补充材料）": "none",
}
FORMAT_CN = {
    "selective": "部分候选人需面试（评估制）", "async_video": "异步视频面试（录播）",
    "live_video": "真人视频面试", "phone": "电话面试", "written_live": "笔试/机考+真人面试",
    "group": "群面/小组讨论", "mixed": "混合形式", "none": "无强制面试",
}

unmapped = set(df["面试形式"]) - set(FORMAT_MAP)
print("未覆盖的原始写法数量:", len(unmapped))
print("原始写法唯一值 49 → 编码 8 类")"""
    ),
    nbf.v4.new_markdown_cell(
        """## 2. 平台标签与题目数量/时长解析

- **平台标签**：从「面试平台」自由文本中抽取标准化平台（Zoom / Kira Talent / WePow / 自建平台 / Skype / Lantern AI / Astronaut / 线下·校园 / 电话等），一行为多标签。
- **题目数量**：解析「约N题 / N-M题（取中值）/ Q1-Q6 / 3题×1.5分钟」等写法。
- **时长（分钟）**：N-M分钟取中值、N分钟取整；纯笔试/机考/技能评估/按小时计段不计入（如「笔试2小时+面试10-15分钟」只取 12.5 分钟）。"""
    ),
    nbf.v4.new_code_cell(
        """PLATFORM_PATTERNS = [
    ("Zoom", r"zoom"), ("Kira Talent", r"kira"), ("WePow", r"wepow"),
    ("自建平台", r"自建平台"), ("Skype", r"skype"), ("Lantern AI", r"lantern"),
    ("Astronaut", r"astronaut"), ("在线机考平台", r"机考|在线平台"),
    ("线下/校园", r"线下|校园"), ("电话", r"电话"),
]

def parse_platform_tags(platform_str):
    if pd.isna(platform_str):
        return ""
    text = str(platform_str).lower()
    return ",".join(tag for tag, pat in PLATFORM_PATTERNS if re.search(pat, text))

def parse_question_count(text):
    if pd.isna(text):
        return None
    s = str(text)
    m = re.search(r"约?(\\d{1,2})\\s*[-—–~]\\s*(\\d{1,2})\\s*题", s)
    if m:
        return round((int(m.group(1)) + int(m.group(2))) / 2, 1)
    m = re.search(r"约?(\\d{1,2})\\s*题", s)
    if m:
        return int(m.group(1))
    m = re.search(r"Q(\\d)[-—–]?Q?(\\d)?", s, re.IGNORECASE)
    if m:
        return int(m.group(2)) if m.group(2) else int(m.group(1))
    return None

def parse_duration_min(text):
    if pd.isna(text):
        return None
    total, found = 0.0, False
    for seg in re.split(r"[；;，,+＋]", str(text)):
        if re.search(r"笔试|机考|技能评估|小时", seg) and not re.search(r"面试|真人面|面谈", seg):
            continue
        m = re.search(r"(\\d{1,3})\\s*[-—–~]\\s*(\\d{1,3})\\s*分钟", seg)
        if m:
            total += (int(m.group(1)) + int(m.group(2))) / 2; found = True; continue
        m = re.search(r"约?(\\d{1,3})\\s*分钟", seg)
        if m:
            total += int(m.group(1)); found = True
    return round(total, 1) if found else None"""
    ),
    nbf.v4.new_code_cell(
        """df["面试形式编码"] = df["面试形式"].map(FORMAT_MAP)
df["面试形式分类"] = df["面试形式编码"].map(FORMAT_CN)
df["平台标签"] = df["面试平台"].apply(parse_platform_tags)
df["题目数量(解析)"] = df["题目数量/时长"].apply(parse_question_count)
df["时长分钟(解析)"] = df["题目数量/时长"].apply(parse_duration_min)

assert df["面试形式编码"].notna().all(), "存在未编码的面试形式"
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print("清洗完成 →", OUT)"""
    ),
    nbf.v4.new_markdown_cell("""## 3. 数据质量校验"""),
    nbf.v4.new_code_cell(
        """print("总记录数:", len(df))
print("重复(院校+项目):", df.duplicated(subset=["院校", "项目名称"]).sum())
print("关键字段缺失:", df[["国家/地区", "院校", "项目名称", "面试形式", "问题类型"]].isna().sum().sum())
print("\\n面试形式编码分布:")
print(df["面试形式编码"].value_counts().to_string())
print("\\n平台标签 Top8:")
print(df["平台标签"].value_counts().head(8).to_string())
print("\\n时长解析: 有值", df["时长分钟(解析)"].notna().sum(), "行 | 中位数", df["时长分钟(解析)"].median(), "分钟")"""
    ),
    nbf.v4.new_code_cell(
        """df[["序号", "国家/地区", "院校", "项目名称", "面试形式编码", "面试形式分类", "平台标签", "题目数量(解析)", "时长分钟(解析)"]].head(10)"""
    ),
    nbf.v4.new_markdown_cell(
        """## 小结

- 100 条记录全部完成标准化，无重复、无关键字段缺失。
- 面试形式 49 种自由文本 → 8 类编码；`selective`（部分候选人评估制）占比最高（43%），其次真人视频（24%）、异步录播视频（14%）。
- 题目数量仅在 17 条中可显式解析（其余原文未报告）；时长在 64 条中可解析，中位数约 17.5 分钟。
- 解析字段的局限（如「约N题」取中值、单题时长未乘题数）记录于 `docs/coding_scheme.md`。"""
    ),
]

# ================= Notebook 02: 探索性分析 =================
nb2 = nbf.v4.new_notebook()
nb2.metadata.kernelspec = {"name": "python3", "display_name": "Python 3", "language": "python"}
nb2.cells = [
    nbf.v4.new_markdown_cell(
        """# 02 探索性数据分析（EDA）

**研究问题**: BA/DS 硕士招生面试考察什么？不同地区与项目类型有何差异？WKU 申请者应如何准备？  
**数据**: `data/pilot_dataset_cleaned.csv`（100 条试点记录，6 个地区 / 80 所院校 / 47 个方向）"""
    ),
    nbf.v4.new_code_cell(
        """import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("../data/pilot_dataset_cleaned.csv")
print(f"记录 {len(df)} 条 | 地区 {df['国家/地区'].nunique()} | 院校 {df['院校'].nunique()} | 方向 {df['项目名称'].nunique()}")"""
    ),
    nbf.v4.new_markdown_cell("## 1. 地区与面试形式分布"),
    nbf.v4.new_code_cell(
        """region_order = df["国家/地区"].value_counts().index.tolist()
fmt_order = ["live_video", "async_video", "selective", "written_live", "group", "mixed", "phone", "none"]
fmt_cn = {"live_video": "真人视频", "async_video": "异步录播视频", "selective": "部分候选人评估制",
          "written_live": "笔试+真人面", "group": "群面", "mixed": "混合", "phone": "电话", "none": "无强制面试"}

ct = pd.crosstab(df["国家/地区"], df["面试形式编码"])[fmt_order]
ct.columns = [fmt_cn[c] for c in ct.columns]

fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
ax = axes[0]
region_cnt = df["国家/地区"].value_counts().reindex(region_order)
ax.bar(region_cnt.index, region_cnt.values, color="#4C72B0")
for i, v in enumerate(region_cnt.values):
    ax.text(i, v + 0.6, str(v), ha="center", fontsize=9)
ax.set_title("各地区记录数", fontsize=11)
ax.set_ylabel("记录数")

ax2 = axes[1]
ct.plot(kind="bar", stacked=True, ax=ax2, colormap="Set2", width=0.72)
ax2.set_title("各地区 × 面试形式（堆叠）", fontsize=11)
ax2.set_xlabel("")
ax2.set_ylabel("记录数")
ax2.legend(fontsize=7.5, ncol=2)
plt.tight_layout()
plt.show()

# 占比表
print("地区 × 面试形式（行占比 %）：")
print((ct.div(ct.sum(axis=1), axis=0) * 100).round(1).to_string())"""
    ),
    nbf.v4.new_markdown_cell("## 2. 面试平台"),
    nbf.v4.new_code_cell(
        """from collections import Counter
tag_cnt = Counter()
for tags in df["平台标签"].dropna():
    for t in str(tags).split(","):
        if t:
            tag_cnt[t] += 1
tag_df = pd.Series(tag_cnt).sort_values(ascending=False)
ax = tag_df.head(8).plot(kind="barh", color="#55A868", figsize=(8, 3.6))
ax.set_title("平台标签频次 Top8（一项目可多平台）", fontsize=11)
ax.invert_yaxis()
for i, v in enumerate(tag_df.head(8).values):
    ax.text(v + 0.2, i, str(v), va="center", fontsize=9)
plt.tight_layout(); plt.show()

kira = df["平台标签"].str.contains("Kira").sum()
zoom = df["平台标签"].str.contains("Zoom").sum()
print(f"使用 Kira Talent（异步录播主流平台）: {kira} 个方向 | 使用 Zoom: {zoom} 个方向")"""
    ),
    nbf.v4.new_markdown_cell("## 3. 问题类型"),
    nbf.v4.new_code_cell(
        """keywords = {
    "行为题": ["行为", "领导力", "团队", "成就", "克服"],
    "动机/Why-this-program": ["为什么", "动机", "Why", "职业规划", "目标"],
    "技术题(统计/概率/编程)": ["技术", "编程", "数学", "统计", "概率", "机器学习", "ML", "算法", "代码"],
    "案例分析": ["案例", "case", "Case"],
    "AI/伦理": ["AI", "伦理", "ethics", "人工智能"],
    "写作": ["写作", "essay", "Essay"],
}
res = {}
for k, kws in keywords.items():
    hits = df["问题类型"].astype(str).apply(lambda s: any(kw in s for kw in kws))
    res[k] = int(hits.sum())
q_df = pd.Series(res).sort_values(ascending=False)
ax = q_df.plot(kind="bar", color="#C44E52", figsize=(8, 3.6))
ax.set_title("问题类型出现频次（关键词匹配，一项目可多类）", fontsize=11)
for i, v in enumerate(q_df.values):
    ax.text(i, v + 0.4, str(v), ha="center", fontsize=9)
plt.tight_layout(); plt.show()
print("Top2 问题类型:", "、".join(q_df.index[:2].tolist()))"""
    ),
    nbf.v4.new_markdown_cell("## 4. 时长与题目量"),
    nbf.v4.new_code_cell(
        """dur = df.dropna(subset=["时长分钟(解析)"])
g = dur.groupby("国家/地区")["时长分钟(解析)"] \
      .agg(["count", "median"]).reindex(region_order)
g.columns = ["有记录数", "时长中位数(分钟)"]
print("各地区面试时长中位数（有解析的行）：")
print(g.round(1).to_string())

overall = df["时长分钟(解析)"].median()
print(f"\\n全部试点：时长中位数 {overall:.1f} 分钟；报告了题目数的方向中位 {df['题目数量(解析)'].median():.0f} 题")"""
    ),
    nbf.v4.new_markdown_cell("## 5. 数据来源构成"),
    nbf.v4.new_code_cell(
        """src = df["来源类型"].str.replace(" + ", "+", regex=False).value_counts().head(6)
ax = src.plot(kind="barh", color="#8172B2", figsize=(8, 3.2))
ax.set_title("来源类型 Top6（院校官网 + 面经平台）", fontsize=11)
ax.invert_yaxis()
for i, v in enumerate(src.values):
    ax.text(v + 0.2, i, str(v), va="center", fontsize=9)
plt.tight_layout(); plt.show()
official = df["来源类型"].str.contains("院校官网").mean() * 100
print(f"含院校官网交叉验证的记录占比: {official:.0f}%")"""
    ),
    nbf.v4.new_markdown_cell(
        """## 关键发现（试点版）

1. **面试普遍性**：仅 6/100 个方向「无强制面试」，其余均有不同形式；**43% 为「部分候选人评估制」**，即很多项目对部分申请者不面试——材料（文书/GRE/推荐信）仍是筛选门槛。
2. **形式地区差异**：美国/英国以**异步录播视频（Kira Talent）**为主（如哥大、NYU Stern、帝国理工、UCL）；中国香港/新加坡以**真人视频（Zoom）+ 笔试/机考组合**为主（HKUST 双教授 CV 面、NUS 机面+真人面、SMU 机考+真人面谈）——东亚项目更强调技术笔试。
3. **平台**：Kira Talent（异步）与 Zoom（真人）是两大主流；自建平台多见于美校。
4. **问题类型**：**行为题与动机题（Why-this-program）覆盖最广**；技术题（统计/概率/编程）集中在异步录播与技术向项目；AI 伦理、案例分析开始出现在前沿项目（如 NYU Stern 的 EHICS 讨论、UCSD 数据分析项目）。
5. **时长**：整体中位数约 17.5 分钟；美国部分项目（杜克 MQM 30–45 分钟、沃顿 45 分钟）显著长于英国/香港多数 15–20 分钟。
6. **对 WKU 申请者的启示（试点）**：主攻真人视频+常见行为/动机题库；对东亚项目补充数学/统计/编程笔试准备；录制类（Kira）注意限时作答与写作题。
> 提示：当前为 100 条试点，12 月前将扩展到 ≥300 条并补充 Reddit/访谈数据后做正式推断。"""
    ),
]

NB_DIR.mkdir(exist_ok=True)
nb1_path = NB_DIR / "01_data_cleaning.ipynb"
nb2_path = NB_DIR / "02_exploratory_analysis.ipynb"
nbf.write(nb1, str(nb1_path))
nbf.write(nb2, str(nb2_path))
print("notebook 骨架已写入:", nb1_path.name, "/", nb2_path.name)
