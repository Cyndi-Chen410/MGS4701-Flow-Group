# -*- coding: utf-8 -*-
"""
MGS 4701 W01 Fall 2026 — Track 5 试点数据清洗脚本
将手收集的原始表（pilot_dataset_raw.csv）清洗为标准化的试点数据集：
  * 标准化「面试形式」为 8 类分析编码（见 docs/coding_scheme.md）
  * 从「面试平台」抽取平台标签
  * 从「题目数量/时长」抽取题目数 / 时长（分钟）
  * 校验：100 条记录、无重复、无关键缺失
"""
import re
import pandas as pd

RAW = "data/pilot_dataset_raw.csv"
OUT = "data/pilot_dataset_cleaned.csv"

# ---------------- 面试形式 → 分析编码（与 coding_scheme.md 保持一致） ----------------
FORMAT_MAP = {
    "部分候选人面试（评估制）": "selective",
    "部分候选人受邀面试": "selective",
    "部分项目需面试": "selective",
    "部分申请者需面试": "selective",
    "部分申请者获邀面试": "selective",
    "材料审核+部分面试": "selective",
    "有面试环节": "selective",
    "行为面试（部分候选人）": "selective",
    "行为面试（邀请制）": "selective",
    "部分项目需面试（研究型MPhil/MRes必面）": "selective",
    "邀请制面试（校园/电话/视频）": "selective",
    "虚拟面试（邀请制）": "selective",
    "部分候选人面试（评估制）": "selective",
    "异步视频面试（录播）": "async_video",
    "视频面试（录播）": "async_video",
    "案例分析视频面试": "async_video",
    "真人视频面试（1V1）+ 视频提交": "live_video",
    "真人视频面试（Zoom/Skype）": "live_video",
    "真人视频面试（推荐参加）": "live_video",
    "真人视频面试（Zoom）+ 技能评估": "live_video",
    "视频面试（部分申请者获邀）": "live_video",
    "视频面试（Zoom）": "live_video",
    "视频面试（Zoom）+ 编程测试": "live_video",
    "视频面试（Zoom/Skype）": "live_video",
    "线上Zoom面试（双教授）": "live_video",
    "全英文个面": "live_video",
    "真人线上单面": "live_video",
    "线上面试": "live_video",
    "结构化面试": "live_video",
    "结构化面试+案例问题": "live_video",
    "面试+写作": "live_video",
    "电话/Skype面试": "phone",
    "视频会议或电话": "live_video",
    "线上机考 + 真人面谈": "written_live",
    "全英文个面（笔试+面试）": "written_live",
    "笔试+面试": "written_live",
    "两轮面试：机面+真人面": "written_live",
    "真人单面 + 笔试": "written_live",
    "小群面": "group",
    "小组讨论(TBD) + 一对一面试": "group",
    "Video / 真人单面 / 群面": "mixed",
    "Video / 真人面 / 群面": "mixed",
    "真人线上面试（单面+群面）": "mixed",
    "无强制面试（需提交GRE/GMAT）": "none",
    "无强制面试（需提交GMAT/GRE）": "none",
    "无强制面试（需提交文书+推荐信）": "none",
    "无强制面试（可选提交补充材料）": "none",
}

FORMAT_CN = {
    "selective": "部分候选人需面试（评估制）",
    "async_video": "异步视频面试（录播）",
    "live_video": "真人视频面试",
    "phone": "电话面试",
    "written_live": "笔试/机考+真人面试",
    "group": "群面/小组讨论",
    "mixed": "混合形式",
    "none": "无强制面试",
}

PLATFORM_PATTERNS = [
    ("Zoom", r"zoom"),
    ("Kira Talent", r"kira"),
    ("WePow", r"wepow"),
    ("自建平台", r"自建平台"),
    ("Skype", r"skype"),
    ("Lantern AI", r"lantern"),
    ("Astronaut", r"astronaut"),
    ("在线机考平台", r"机考|在线平台"),
    ("线下/校园", r"线下|校园"),
    ("电话", r"电话"),
]


def parse_platform_tags(platform_str):
    """从面试平台字段抽取标准化平台标签（逗号分隔）。"""
    if pd.isna(platform_str):
        return ""
    text = str(platform_str).lower()
    tags = []
    for tag, pattern in PLATFORM_PATTERNS:
        if re.search(pattern, text):
            tags.append(tag)
    return ",".join(tags)


def parse_question_count(text):
    """从题目数量/时长抽取题目数：约N题 / N-M题(取中值) / Q1-Q6 / 3题×1.5分钟"""
    if pd.isna(text):
        return None
    s = str(text)
    # 区间优先：约8-9题 → 8.5
    m = re.search(r"约?(\d{1,2})\s*[-—–~]\s*(\d{1,2})\s*题", s)
    if m:
        return round((int(m.group(1)) + int(m.group(2))) / 2, 1)
    m = re.search(r"约?(\d{1,2})\s*题", s)
    if m:
        return int(m.group(1))
    m = re.search(r"Q(\d)[-—–]?Q?(\d)?", s, re.IGNORECASE)
    if m:
        return int(m.group(2)) if m.group(2) else int(m.group(1))
    return None


def parse_duration_min(text):
    """
    从题目数量/时长抽取面试总时长（分钟）：N-M分钟取中值，N分钟取整；
    丢弃纯笔试/机考/技能评估/按小时计段的时长（如 笔试2小时、1小时技能评估）。
    """
    if pd.isna(text):
        return None
    s = str(text)
    total = 0.0
    found = False
    for seg in re.split(r"[；;，,+＋]", s):
        # 不含“面试/真人面/面谈”字样的笔试、机考、技能评估、按小时段不计入
        if re.search(r"笔试|机考|技能评估|小时", seg) and not re.search(r"面试|真人面|面谈", seg):
            continue
        m = re.search(r"(\d{1,3})\s*[-—–~]\s*(\d{1,3})\s*分钟", seg)
        if m:
            total += (int(m.group(1)) + int(m.group(2))) / 2
            found = True
            continue
        m = re.search(r"约?(\d{1,3})\s*分钟", seg)
        if m:
            total += int(m.group(1))
            found = True
    return round(total, 1) if found else None


def main():
    df = pd.read_csv(RAW)
    assert len(df) == 100, f"原始记录数异常: {len(df)}"

    df["面试形式编码"] = df["面试形式"].map(FORMAT_MAP)
    df["面试形式分类"] = df["面试形式编码"].map(FORMAT_CN)
    df["平台标签"] = df["面试平台"].apply(parse_platform_tags)
    df["题目数量(解析)"] = df["题目数量/时长"].apply(parse_question_count)
    df["时长分钟(解析)"] = df["题目数量/时长"].apply(parse_duration_min)

    unmapped = df[df["面试形式编码"].isna()]
    if len(unmapped):
        print("警告：未映射的面试形式：\n", unmapped["面试形式"].unique())
        raise SystemExit(1)

    # 校验
    assert df["面试形式编码"].notna().all(), "存在未编码的面试形式"
    dups = df.duplicated(subset=["院校", "项目名称"]).sum()
    missing_key = df[["序号", "国家/地区", "院校", "项目名称", "面试形式", "问题类型"]].isna().sum().sum()
    print(f"记录数: {len(df)} | 重复(院校+项目): {dups} | 关键字段缺失: {missing_key}")
    print(f"面试形式编码分布:\n{df['面试形式编码'].value_counts().to_string()}")

    df.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"已输出: {OUT}")


if __name__ == "__main__":
    main()
