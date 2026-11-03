import json, sys, csv
sys.path.insert(0,'A2_repository/code')
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import docx_helpers as H
import analysis as A

rows=A.load(); S=A.summarize(rows); N=S['N']
R=S['by_region']
V=json.load(open('work/validation_results.json'))
CODER={'doc_all':(150,0.800,0.571,0.448,0.693),'doc_text':(54,0.889,0.725,0.492,0.911),
       'format':(37,0.189,0.123,0.041,0.215),'platform':(31,0.097,0.076,0.000,0.159)}
by=S['by_region']
has=[r for r in rows if r['has_interview']]
fmt={}
for r in has: fmt[r['format_primary']]=fmt.get(r['format_primary'],0)+1
doc_formats=sum(v for k,v in fmt.items() if k not in ('Unknown','None'))

doc=Document(); H.setup(doc)
doc.core_properties.title='What 150 BA and Data Science Master\u2019s Programmes Actually Tell Applicants About Interviews'
doc.core_properties.author='Chen Xinling; Xu Chi; Shen Zhehao'
doc.core_properties.subject='MGS 4701 Track 5 A2 findings report'
# page number footer
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH
footer=doc.sections[0].footer.paragraphs[0]
footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
run=footer.add_run()
fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE')
run._r.addnext(fld)

H.title_page(doc,
 'What 150 BA and Data Science Master\u2019s Programmes Actually Tell Applicants About Interviews',
 'A2 \u2014 Analysis-ready dataset, validation and exploratory findings (Track 5)',
 ['MGS 4701 W01 \u00b7 Fall 2026 \u00b7 Group project, Track 5',
  'Chen Xinling \u00b7 Xu Chi \u00b7 Shen Zhehao',
  '29 October 2026',
  'Repository: github.com/Cyndi-Chen410/MGS4701-Flow-Group'])

# 1
H.h1(doc,'1. Question, and what changed since A1')
H.para(doc,'Our question is now: **which Business Analytics (BA) and Data Science (DS) master\u2019s programmes operate an interview stage, in what format, and what does the verifiable public record say they assess?** The audience and the decisions are unchanged. We are WKU students choosing where to apply in October\u2013December 2026, and we need to know (i) whether a programme interviews at all, (ii) what kind of preparation that implies, and (iii) how far the available evidence can be trusted before we spend weeks rehearsing the wrong thing.')
H.para(doc,'Two things changed. First, we rebuilt the dataset. A link audit of the A1 pilot found that only 25 of its 100 source URLs returned a readable page, that 18 were dead and the rest blocked automated access, and that 22 of the 25 readable pages were generic programme pages containing no interview statement. Twenty-two rows also shared an identical duration string and 32 shared an identical three-question template. The A1 claim that 100% of rows had been cross-validated against the official page is therefore not supported, and we replaced the pilot with 150 records that were collected and checked again between 20 and 29 October 2026 (Section 2).')
H.para(doc,'Second, the outcome changed from \u201cwhat interviews examine\u201d to \u201cwhat is documented about interviews\u201d. A1 assumed that interview format and question content are publicly observable. They are not: for 85 of 150 programmes (57%) no official or public page states whether an interview exists. That is itself the most decision-relevant finding for an applicant, and it forces us to separate what is known (prevalence, format where stated) from what is asserted in unpaid advice posts (question lists). The report therefore answers the narrower question that the evidence can carry, and says explicitly where it cannot.')

# 2
H.h1(doc,'2. Dataset')
H.para(doc,f'The analysis file contains **{N} programmes at {S["schools"]} schools** across six regions, collected 20\u201329 October 2026 (Table 1). The unit is one taught master\u2019s programme; a school appears more than once only when it runs distinct programmes. The sampling frame is purposive: every programme named in the A1 pilot that still exists, plus replacements for programmes that had been renamed, discontinued or mis-specified, and additional programmes needed to reach 150. Inclusion required a live official programme or admissions page. We excluded executive, part-time and online-only variants, and pure finance or accounting degrees, because their interview practice is not comparable to the full-time route our audience applies to.')
H.caption(doc,'Table 1. Coverage by region. \u201cInterview\u201d = required or invitation-only stage; \u201cdocumented\u201d = any statement that an interview exists or explicitly does not. Intervals are 95% Wilson intervals.')
reg_rows=[]
for reg in A.REGIONS:
    d=by[reg]
    reg_rows.append([A.LABEL[reg],d['n'],d['schools'],d['k'],f"{d['pct']*100:.0f}% ({d['lo']*100:.0f}\u2013{d['hi']*100:.0f})",f"{d['doc_pct']*100:.0f}%"])
reg_rows.append(['Total',N,S['schools'],S['has'],f"{S['has']/N*100:.0f}%",f"{S['documented']/N*100:.0f}%"])
H.table(doc,['Region','Programmes','Schools','Interview (n)','Share (95% CI)','Documented'],reg_rows,widths=[3.4,2.0,1.7,2.1,3.2,2.2],font=8.6)
H.para(doc,'',space_after=2)

H.h2(doc,'2.1 What the A1 pilot contained')
H.para(doc,'The audit matters for how much of A1 can be reused, so we report it precisely. Of the 100 A1 rows, 18 URLs were dead (404, DNS failure or malformed host), 57 were blocked to automated access, and 25 returned readable text. Of those 25, only three pages mentioned an interview; the other 22 were programme home pages. Several programmes had also been renamed or mis-specified: Northwestern\u2019s MS in Analytics is now the MS in Machine Learning and Data Science, Imperial\u2019s is now MSc Business Analytics & AI, and five rows were finance or accounting degrees outside the frame. We retained the research question and audience but not the pilot\u2019s interview fields.')
H.para(doc,f'The rebuilt file records, for every row, the official URL, the verbatim evidence sentence (where one exists) and its URL, whether the evidence is official or third-party, and whether the URL and quote were re-checked against the live page. In total {sum(1 for r in rows if r["verified_url"]=="1")} of 150 official URLs returned content in the October audit; {sum(1 for r in rows if r["verified_quote"]=="1")} verbatim evidence quotes were matched against the retrieved page text, and {S["third_party"]} interview records rest on a named public interview-experience page rather than the university.')

H.h2(doc,'2.2 What is missing, and why it matters')
H.para(doc,f'Three gaps dominate. First, **silence**: only {S["documented"]} programmes have any statement about interviews, and {N-S["documented"]} have none. \u201cNot stated\u201d is not \u201cno interview\u201d; it means the public record does not settle the question, and we never code it as a negative. Second, **thin detail**: of the {S["has"]} programmes with an interview stage, only {doc_formats} state a format, 11 state a duration, six state a question count, and 11 have any verbatim example question. Third, **coverage**: Australia contributes {R["AU"]["n"]} programmes and no documented interview; Singapore contributes {R["SG"]["n"]} programmes and Macao {R["MO"]["n"]}, so those regional estimates are imprecise. Third-party evidence is concentrated in Hong Kong and the United States and is dated between 2020 and 2025, so it may describe an older cycle. These gaps are the reason the findings below distinguish prevalence from format and from question content.')

# 3
H.h1(doc,'3. Validation')
H.para(doc,'We validated two things: whether a rule-based extractor can reproduce a human coding of the page text, and whether two coders agree with each other. The gold set is the full 150-record file, hand-coded under codebook v2.0 (repository: docs/codebook.md). Each record was coded for interview status (required / invitation-only / not required / not stated), format, platform, and up to seven assessment-focus flags. Coding rules were written before coding and applied to all 150 records; \u201cnot stated\u201d is a code, not a missing value.')
H.h2(doc,'3.1 Automated extraction versus hand coding')
H.para(doc,'The automated arm applies fixed lexical rules to the retrieved evidence: it looks for admission-interview phrases, then maps modality words (Kira, asynchronous, recorded, Zoom, panel, group, test) and platform names. It is deliberately simple and reproducible; the notebook that runs it is in the repository (code/validation.py). Table 2 reports agreement with the hand-coded gold set.')
H.caption(doc,'Table 2. Agreement between rule-based extraction and hand coding. \u03ba = Cohen\u2019s kappa; intervals are 2,000-sample bootstrap 95% intervals.')
vd=V['documented']; vf=V['format']; vp=V['platform']
H.table(doc,['Comparison','n','Agreement','\u03ba (95% CI)'],
 [['Interview documented (binary)',vd['n'],f"{vd['accuracy']*100:.0f}%",f"{vd['kappa']:.2f} ({vd['ci'][0]:.2f}\u2013{vd['ci'][1]:.2f})"],
  ['Format (5 categories)',vf['n'],f"{vf['accuracy']*100:.0f}%",f"{vf['kappa']:.2f} ({vf['ci'][0]:.2f}\u2013{vf['ci'][1]:.2f})"],
  ['Platform (5 categories)',vp['n'],f"{vp['accuracy']*100:.0f}%",f"{vp['kappa']:.2f} ({vp['ci'][0]:.2f}\u2013{vp['ci'][1]:.2f})"]],
 widths=[6.6,1.5,2.4,4.2],font=8.6)
H.para(doc,'',space_after=2)
H.para(doc,f'The extractor never produced a false positive ({vd["fp"]} cases) but missed {vd["fn"]} of the {S["documented"]} documented programmes, a recall of {vd["tp"]/S["documented"]*100:.0f}%. The misses are informative rather than random: pages phrase interviews as \u201cshortlisted candidates may be invited\u201d, \u201cselected applicants will be contacted\u201d or \u201can interview may be requested\u201d, none of which match a rule that expects an explicit admission-interview construction. Format agreement is moderate because many pages state that an interview exists without naming its modality; platform agreement is similar. The practical conclusion is that automated extraction is a useful screening tool but not a substitute for reading the page: it is precise enough to trust a positive, and too conservative to trust a negative.')
H.h2(doc,'3.2 Inter-coder agreement')
H.para(doc,'A second coder (an AI coder; see AI log), working only from the codebook and a blind packet of the retrieved evidence passages (no access to the first coder\u2019s labels), coded all 150 records for interview status, format and platform. Agreement on whether an interview is documented at all was substantial: 80% raw agreement, \u03ba = 0.57 (95% CI 0.45\u20130.69); on the 54 records whose packet contained interview text, \u03ba = 0.73 (0.49\u20130.91). Agreement on format was poor (\u03ba = 0.12, n = 37) and on platform no better (\u03ba = 0.08, n = 31).')
H.para(doc,'The disagreement is concentrated exactly where the data are weakest. The second coder coded generic \u201conline interview\u201d or \u201cvideo interview\u201d as Unknown because the excerpt does not establish whether the interview was live or recorded; the first coder, reading the full page and the programme\u2019s practice, coded many as live. The second coder also had no text at all for 96 records, because the official pages are JavaScript-rendered or blocked and the archived excerpt was empty. That is not coder error: it shows that the archived evidence packet, not the programme, is the binding constraint.')
H.para(doc,f'Implication for the findings: **prevalence is the robust variable** (both coders, and the rule-based extractor, agree that roughly four in ten programmes document an interview); **format is fragile** and should be read as a description of the {doc_formats} programmes whose sources name a modality, not as a population share; **question content is anecdotal**, with 11 programmes contributing verbatim questions, mostly from third-party posts. We therefore report format as counts with denominators, never as a single percentage for \u201call programmes\u201d, and we do not present a question bank in this report.')
H.para(doc,'Two boundary disagreements are worth recording because they recur. First, \u201cno interview\u201d versus \u201cnot required\u201d: CUHK\u2019s FinTech FAQ says \u201cNo interview is required for our programmes\u201d, which we code as no interview, whereas \u201cinterviews may be requested\u201d is coded as invitation-only. Second, video essay versus interview: Michigan State requires a rotating video essay inside the application portal. We code it as an asynchronous assessment and flag it, but a reader who reserves \u201cinterview\u201d for a human interaction would code it differently. Both are documented in the notes field so that the alternative coding can be reconstructed.')

# 4
H.h1(doc,'4. Findings')
H.h2(doc,'Finding 1 \u2014 Interviews are a minority practice, and they cluster in Hong Kong and the United States')
H.para(doc,f'Sixty of 150 programmes ({S["has"]/N*100:.0f}%, 95% CI 32\u201348%) document an interview stage, and five explicitly state that none is required. The regional spread is wide (Figure 1). Hong Kong is the outlier: {R["HK"]["k"]} of {R["HK"]["n"]} programmes ({R["HK"]["pct"]*100:.0f}%) interview, and only {R["HK"]["n"]-R["HK"]["documented"]} are silent. In the United States, {R["US"]["k"]} of {R["US"]["n"]} ({R["US"]["pct"]*100:.0f}%) interview, but the practice is concentrated in private business schools and analytics programmes; large public data-science degrees often admit on documents alone. The United Kingdom is the opposite of its reputation: only {R["UK"]["k"]} of {R["UK"]["n"]} programmes ({R["UK"]["pct"]*100:.0f}%) document an interview, and {R["UK"]["n"]-R["UK"]["documented"]} are silent. Australia is uniformly silent: none of its {R["AU"]["n"]} programmes states an interview, and none states that there is no interview either. Singapore ({R["SG"]["k"]} of {R["SG"]["n"]}) and Macao ({R["MO"]["k"]} of {R["MO"]["n"]}) are too small to support regional claims.')
H.figure(doc,'A2_repository/figures/fig1_prevalence.png',6.25)
H.caption(doc,'Figure 1. Share of programmes with a documented interview stage, by region, with 95% Wilson intervals.')
H.para(doc,'This is the first decision-relevant result. An applicant who assumes that a BA/DS master\u2019s always involves an interview will over-prepare for the United Kingdom and Australia and under-prepare for Hong Kong. It also explains why advice posts disagree: they generalise from a handful of interview-heavy programmes to a population in which most programmes do not interview, or do not say.')

H.h2(doc,'Finding 2 \u2014 Among programmes that name a format, asynchronous video and live interviews are evenly split')
H.para(doc,f'Of the {doc_formats} programmes whose source names a modality, 17 use asynchronous recorded video (Kira or a school platform), 15 use a live one-to-one interview, four use a panel, and one uses a test (Figure 2). The remaining {S["has"]-doc_formats} interviewing programmes say only that \u201can interview\u201d takes place. The split matters for preparation because the two formats reward different behaviour: asynchronous answers are short, timed and unresponsive to the interviewer; live interviews allow follow-up and are where technical probing happens.')
H.figure(doc,'A2_repository/figures/fig2_format.png',6.25)
H.caption(doc,f'Figure 2. Format among the {doc_formats} programmes that state one. {S["has"]-doc_formats} further programmes document an interview but not its format.')
H.para(doc,'The regional pattern is consistent with the qualitative record. Asynchronous video is the default in the United States (13 of 23 formatted US programmes) and in the United Kingdom (three of four); Hong Kong is the live-interview market (five live one-to-one and two panels out of seven formatted programmes, with no asynchronous format); Singapore’s two formatted programmes are one test and one asynchronous video, and Macao’s single formatted programme is a panel. Named platforms are rare: Kira Talent appears six times, Zoom six, a school platform five, telephone twice and in-person four times; 37 interviewing programmes name no platform. Platform is therefore a weaker signal than format, and applicants should prepare for the format rather than the vendor.')

H.h2(doc,'Finding 3 \u2014 Motivation and behavioural questions dominate; technical and case questions are less common than the advice literature suggests')
H.para(doc,f'Across the {S["has"]} interviewing programmes, the assessment focus coded from the source is motivation and fit (16 programmes, 27%), behavioural evidence (16, 27%), technical or quantitative probing (12, 20%), self-introduction or CV walk-through (7, 12%), a written component (4, 7%), a business case (2, 3%) and ethics (1, 2%). Figure 3 shows the distribution. The result is not that technical questions are unimportant \u2014 they are decisive where they occur \u2014 but that they are not the modal content of a BA/DS interview.')
H.figure(doc,'A2_repository/figures/fig3_focus.png',6.25)
H.caption(doc,'Figure 3. Assessment focus coded from programme pages and named interview accounts (multi-label; n = 60 interviewing programmes).')
H.para(doc,'Case interviews, which dominate MBA preparation advice, are almost absent from the BA/DS record: two programmes. Ethics appears once as an assessed dimension, despite the frequency with which AI ethics is discussed in programme marketing. Applicants should not spend their scarce preparation time on case frameworks or ethics essays unless a specific programme\u2019s page names them.')

H.h2(doc,'Finding 4 \u2014 BA programmes interview more often; DS programmes interview less but test technical content harder')
H.para(doc,'The degree type splits the sample cleanly (Table 3). BA programmes interview at 49% (38 of 78), DS programmes at 23% (13 of 56), and analytics-adjacent degrees (statistics, fintech, information systems) at 56% (9 of 16). Among programmes that interview, DS interviews are far more likely to include technical probing (6 of 13, 46%) than BA interviews (2 of 38, 5%), while BA interviews are more likely to include behavioural and motivational content. This is the closest thing in the data to a preparation rule: the letter after the degree predicts the content of the interview more reliably than the region does.')
H.caption(doc,'Table 3. Interview practice by degree type.')
H.table(doc,['Degree type','Programmes','Interview','Async video','Technical focus','Behavioural focus'],
 [['BA (business analytics)',78,'38 (49%)','15','2','9'],
  ['DS (data science)',56,'13 (23%)','2','6','6'],
  ['Adjacent (stats/fintech/IS)',16,'9 (56%)','0','4','1']],
 widths=[5.6,2.3,2.3,2.1,2.4,2.5],font=8.6)
H.para(doc,'',space_after=2)

H.h2(doc,'Finding 5 \u2014 The public record is thin, and third-party accounts fill the gap unevenly')
H.para(doc,f'Figure 4 separates official statements from third-party accounts and from silence. {S["has"]-S["third_party"]} interviewing programmes are documented on an official page; {S["third_party"]} rest on a named public interview account (ChaseDream, Gter, Zhihu, consultancy pages) and {N-S["documented"]} programmes have no statement at all. The regional difference is stark: {R["HK"]["doc_pct"]*100:.0f}% of Hong Kong programmes are documented, against {R["US"]["doc_pct"]*100:.0f}% in the United States, {R["UK"]["doc_pct"]*100:.0f}% in the United Kingdom and {R["AU"]["doc_pct"]*100:.0f}% in Australia. Where official pages are silent, third-party accounts are concentrated in Hong Kong and the United States; for the United Kingdom they were largely unavailable or did not name the programme.')
H.figure(doc,'A2_repository/figures/fig4_disclosure.png',6.25)
H.caption(doc,'Figure 4. How interview information is documented, by region.')
H.para(doc,'This is the finding that most changes our advice. The absence of an official statement is not evidence that a programme does not interview; it is evidence that the applicant cannot know without asking. For the 85 silent programmes the practical recommendation is to email admissions and ask three questions: is there an interview stage, is it live or recorded, and what does it assess. That is a two-minute action that resolves more uncertainty than another hour of reading advice posts.')

# 5
H.h1(doc,'5. Working answer')
H.para(doc,'Our current answer has three parts. **First, treat the interview as a conditional stage, not a default.** Across 150 programmes, 40% document one, 57% say nothing and 3% explicitly do not require one. Hong Kong is the interview market; Australia is not; the United Kingdom is less interview-heavy than its business schools\u2019 reputations imply. **Second, prepare for the format the programme names.** Where a format is stated it is almost equally likely to be asynchronous video or live, and the two require different practice: timed 60\u201390-second recorded answers for Kira-style stages, and conversational follow-up, CV defence and technical probing for live stages. **Third, expect motivation and behavioural questions first, technical questions second and case or ethics questions rarely.** The degree type sharpens this: DS interviews are technical; BA interviews are behavioural.')
H.para(doc,'For a WKU applicant with limited time, the allocation that follows is: one week of behavioural and motivation stories (STAR), one week of CV and project defence including the maths behind the project, two days of timed asynchronous practice, and one day of programme-specific research to establish whether an interview exists at all. Case frameworks and ethics essays are not a priority unless a named programme assesses them.')
H.para(doc,'**What would show us we were wrong.** (1) A re-check of 30 randomly chosen \u201cnot stated\u201d programmes that finds an interview stage at 40% or more of them would invalidate the prevalence estimate, because silence would then be a documentation artefact rather than a programme characteristic. (2) A public interview account for an Australian programme that names the programme and describes an interview would break the Australian zero. (3) A full-text second coding that raises format kappa above 0.6 while shifting the asynchronous/live split by more than 15 percentage points would make Finding 2 unsafe. (4) A programme-level question bank showing technical questions in more than half of BA interviews would overturn Finding 3. We regard (1) and (3) as the most likely failures, and both are cheap to test before the final report.')

# 6
H.h1(doc,'6. AI use log and references')
H.h2(doc,'AI use log')
H.para(doc,'AI (Claude, through a coding agent) was used for: (i) retrieving and summarising official programme pages and public interview accounts, with every row required to carry a verbatim quote and URL; (ii) writing the cleaning, extraction, validation and charting code; (iii) serving as the second, blind coder in Section 3.2; and (iv) drafting and editing this report. No row was accepted on the model\u2019s memory: every retained row has an official URL, and every evidence quote was checked against the retrieved page where the page was retrievable. Rows whose programme could not be verified, or whose name no longer exists, were replaced rather than filled. The A1 audit in Section 2.1 was run by script against the live URLs. The second coder was an AI, not a human; its agreement with the first coder measures codebook clarity and the adequacy of the evidence packet, not human\u2013human reliability, and a human second coder should replace it before submission. All prompts and the coding packet are in the repository.')
H.h2(doc,'References')
for t in [
 'Cohen, J. (1960). A coefficient of agreement for nominal scales. Educational and Psychological Measurement, 20(1), 37\u201346.',
 'Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159\u2013174.',
 'Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. Journal of the American Statistical Association, 22(158), 209\u2013212.',
 'Kira Talent (2026). Asynchronous video interviewing in graduate admissions. kira.talent.',
 'MGS 4701 (2026). Group Project Instructions, Track 5; A1 project brief (Chen, Xu & Shen).',
 'Programme pages and interview accounts: 150 source URLs are listed in the dataset (data/interview_programs_150.csv, fields official_url and evidence_url).']:
    H.para(doc,t,size=9,space_after=3)

doc.save('A2_Findings_Report_ShenZhehao.docx')
print('saved')
