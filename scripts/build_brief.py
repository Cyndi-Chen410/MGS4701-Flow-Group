# -*- coding: utf-8 -*-
"""生成 Project Brief (.docx) — 标题页 + 正文(≤4页)，再经 Word COM 转存为 .doc"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from pathlib import Path

OUT_DOCX = Path(__file__).resolve().parent.parent / "MGS4701_Track5_Project_Brief.docx"

doc = Document()

# 全局样式
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(10.5)
style.paragraph_format.space_after = Pt(4)
for section in doc.sections:
    section.top_margin = Cm(1.8)
    section.bottom_margin = Cm(1.8)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)


def heading(text, size=12, before=8):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor(0x1F, 0x3B, 0x66)
    return p


def para(text, bold=False, italic=False, size=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    if size:
        r.font.size = Pt(size)
    return p


def bullet(text, level=0):
    p = doc.add_paragraph(style="List Bullet")
    if level:
        p.paragraph_format.left_indent = Cm(0.7 * level)
    p.add_run(text)
    p.paragraph_format.space_after = Pt(2)
    return p


def table(rows, widths=None, header=True):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Light Grid Accent 1"
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.text = ""
            r = cell.paragraphs[0].add_run(val)
            r.font.size = Pt(9.5)
            if header and i == 0:
                r.bold = True
    if widths:
        for j, w in enumerate(widths):
            for row in t.rows:
                row.cells[j].width = Cm(w)
    return t


# ================= 标题页 =================
for _ in range(3):
    doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("MGS 4701 W01 Fall 2026 — Final Project Brief")
r.bold = True; r.font.size = Pt(16); r.font.color.rgb = RGBColor(0x1F, 0x3B, 0x66)

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Admission Interviews for Master's Programs in Business Analytics and Data Science:\nWhat Programs Ask and How WKU Applicants Should Prepare")
r.bold = True; r.font.size = Pt(13)

doc.add_paragraph()
table([
    ["Project title", "Admission Interviews for MS in Business Analytics / Data Science: What Programs Ask and How WKU Applicants Should Prepare (Track 5)"],
    ["Team members", "Chen Xinling / Xu Chi / Shen Zhehao"],
    ["Research question", "What do BA/DS master's admission interviews examine? How do interview formats and question types differ across regions and program types? How should WKU applicants prepare, based on verifiable evidence?"],
    ["GitHub repository", "https://github.com/Cyndi-Chen410/MGS4701-Flow-Group.git"],
], widths=[4.5, 12.5])

doc.add_page_break()

# ================= 正文 =================
heading("1. Question and Audience")
para("Our research question: What do admissions interviews for Master's programs in Business Analytics (BA) and Data Science (DS) examine, how do they differ across regions and program types, and how should WKU applicants prepare on the basis of verifiable evidence rather than hearsay?")
para("The audience is ourselves: WKU students planning BA/DS graduate applications for Fall 2026/2027 intake, with the decision timeline of October–December 2026. Our findings will support three decisions: (1) which programs require interviews and in what format; (2) which interview question banks (motivation, behavioral, technical, case, AI-ethics) to practice for each program type; and (3) how to budget preparation time, including whether a written/machine-test component exists.")
para("By \u201cinterview\u201d we mean any structured evaluation beyond the written application: live or pre-recorded video interviews, phone screens, written or machine tests, group discussions, and invitation-only selection rounds. For each program we record the interview format, platform, number of questions, total duration, and the question types observed in recent cycles. The deliverables are a public code repository with reproducible cleaning and analysis pipelines, an interactive dashboard, a written report, and mock-interview question banks organized by region and program type.")

heading("2. Sampling Frame")
para("Population: taught master's programs in BA, DS, and analytics-oriented degrees offered in the six regions most relevant to WKU applicants — US, UK, Hong Kong SAR, Macau SAR, Singapore, and Australia. Sampling unit: one program (unique school + program name).")
table([
    ["Dimension", "Setting"],
    ["Search terms", "\u201cMS Business Analytics admission interview\u201d, \u201cMSc Data Science interview\u201d, \u201cKira interview\u201d, \u201c[school] 面经 / 面试\u201d (Chinese communities)"],
    ["Time window", "Program pages for the 2026 admission cycle; experience posts published 2023–2025"],
    ["Inclusion criteria", "BA/DS/analytics program; located in the six regions; official page or verifiable post states interview facts (format, platform, question types)"],
    ["Exclusion criteria", "No retrievable interview information; anonymous posts with no verifiable source; non-analytics programs (e.g., pure accounting/finance)"],
], widths=[4.0, 13.0])
para("Rationale: these regions cover the destinations WKU applicants actually target; restricting to verifiable sources is what turns \u201chearsay\u201d into evidence-based preparation advice. Each unique school-plus-program pair counts as one observation, so no program is double-counted; executive-format or heavily part-time variants are excluded because their interview practice differs from the full-time taught route most WKU students pursue. The frame is frozen in the collection protocol, and any future deviation must be logged before the dataset is updated.")

heading("3. Data Collection")
para("Primary data sources: official program admissions pages (interview format, platform, invitation policy) cross-verified with interview-experience posts from Chinese communities (Zhihu, Xiaohongshu, Yimusanfendi, New Oriental, Zhinanzhe). Each of the 100 pilot records carries a source URL and is validated against the official page.")
para("First attempt and fallback ladder (as specified in the Track 5 brief):")
bullet("Try: program admission pages + Reddit r/gradadmissions via its official API.")
bullet("If blocked: manual collection from Xiaohongshu and Yimusanfendi (login-walled; collected manually by hand, no scraping, in compliance with platform terms).")
bullet("Alternative data (last resort): 8–12 semi-structured interviews with WKU alumni and current applicants, planned for December as a triangulation source.")
para("Pilot data composition (collected September 20–25, 2026): exactly 100 records across six regions — United States 40, United Kingdom 18, Hong Kong SAR 18, Singapore 13, Australia 9, Macau SAR 2 — covering 80 schools and 47 program directions. Every record carries a verifiable source URL, and 100% of records were cross-validated against the program's official admissions page; experience posts enriched the question-type and typical-question fields but never replaced official facts. The eight-category format coding scheme and all cleaning steps are versioned in the repository and reproducible end to end.")
para("Execution record: Reddit's API could not be accessed reliably from our network environment (connection blocked/rate-limited), so we triggered the fallback and collected the 100-record pilot from official pages + Chinese experience communities between September 20–25. All records satisfy the \u2265100-row pilot requirement (exactly 100 rows, 6 regions, 80 schools, 47 program directions).")

heading("4. Preliminary Findings (Pilot)")
para("Even at pilot scale, the 100 records already reveal stable patterns that will shape the December expansion:")
bullet("Interviews are nearly universal: 94% of the 47 program directions include an interview stage for at least some candidates; only six directions explicitly state no mandatory interview.")
bullet("Formats cluster by region: US and UK programs widely use asynchronous recorded interviews (Kira Talent); Hong Kong and Singapore favor live video interviews, often combined with written or machine tests — 39% of Singapore records combine a written/machine component with a live interview.")
bullet("Question banks: motivation questions (Why this program) and behavioral questions appear in nearly every region; technical questions (statistics, probability, programming) concentrate in asynchronous formats and technical programs; AI-ethics and case questions are beginning to appear in recent cycles.")
bullet("Duration: the median interview runs about 17.5 minutes, but US programs such as Duke MQM and Wharton MIS run 30–45 minutes.")
bullet("Implications for WKU applicants: prioritize live video practice with behavioral and motivation question banks; add written math/statistics/programming preparation for East Asian programs; for Kira-style interviews, practice timed answers and on-screen writing.")

heading("5. Risk")
para("Risk description: the largest failure mode is that interview information becomes unverifiable or outdated — login walls on Xiaohongshu/Yimusanfendi, quickly-changing program formats, and reliance on anonymous experience posts could produce a dataset that misleads applicants rather than helps them. A second risk is scale: with only 100 pilot rows, regional comparisons (e.g., Australia, Macau) rest on very few observations, so conclusions could overfit anecdotes. A third risk is coding ambiguity: the pilot contained 49 distinct free-text descriptions of interview formats, which the cleaning pipeline maps to an eight-category scheme; the mapping is versioned, and any new phrasing must be added to the format map before re-running the cleaning script, keeping every step reproducible.")
para("Mitigation: every record must pass official-page cross-validation (100% achieved in the pilot); format changes are re-checked against the current cycle before final publication; the sampling frame is frozen in the collection protocol and any deviation is logged; regions with thin coverage (Australia 9, Macau 2) are flagged in analysis and will be expanded to \u2265300 records in the December wave, with alumni interviews as a triangulation source.")

heading("6. Division of Labor")
para("分工占位，请各组员填写：")
table([
    ["Role", "Responsible (name)", "Tasks"],
    ["Collection lead", "Chen Xinling / Xu Chi / Shen Zhehao", "Official pages + community posts; source URLs; interview-form facts"],
    ["Cleaning/coding", "", "Coding scheme; Excel entry; validation against protocol"],
    ["Analysis", "", "Notebooks 01–02; EDA; regional comparisons; charts"],
    ["Writing", "", "This brief; README; final report; AI-use log"],
], widths=[3.5, 4.0, 9.5])

heading("7. AI Use Log")
para("AI (Claude, accessed through a coding agent) was used for: designing and reviewing the cleaning pipeline and coding-scheme implementation; writing and executing the Jupyter notebooks (cleaning + exploratory analysis, including charts); and drafting this brief and the README. All factual content — the 100 records, sources, formats, and question types — was collected manually by the team from the cited pages and posts; AI did not generate or fabricate any data row, and AI-drafted text was checked against the raw collection spreadsheet before inclusion. If additional AI use occurs in later phases (for example, AI-assisted question generation for the mock-interview round), it will be appended here under the same rule: AI may support writing and code, but every fact must trace to the cited sources.")

para("")
para("Word count note: body text ≈ 1,070 words (≈1,300 including title page and tables), within the 4-page limit excluding the title page.", italic=True, size=9)

doc.save(str(OUT_DOCX))
print("saved:", OUT_DOCX)
