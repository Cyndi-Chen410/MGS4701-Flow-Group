# MGS 4701 Track 5 — BA/DS admission interviews (A2 repository)

Dataset, code and validation evidence for the A2 findings report (due 4 November 2026).

## What the data are
`data/interview_programs_150.csv` — one row per taught master's programme (Business Analytics, Data Science, or an analytics-adjacent degree such as statistics/fintech), 150 programmes at 129 schools in six regions: United States (64), United Kingdom (35), Hong Kong SAR (21), Singapore (9), Australia (17), Macao SAR (4).

Collection period: **20–29 October 2026**. Every row was collected or re-checked in that window; the 2027 entry pages were live when checked. Sources are the official programme/admissions page plus, where the official page is silent, one named public interview account (ChaseDream, Gter, Zhihu, study-abroad consultancy). The `evidence_type` field records which.

## Files
| Path | Contents |
|---|---|
| `data/interview_programs_150.csv` | analysis-ready dataset (150 rows, 31 fields) |
| `data/raw_rows.json` | researched rows before coding (raw layer) |
| `data/source_checks.json` | result of the live URL/quote re-check |
| `data/second_coder_codes.json` | blind second-coder labels used for inter-coder agreement |
| `data/validation_results.json` | agreement statistics reproduced by the validation notebook |
| `docs/codebook.md` | coding scheme v2.0 |
| `code/build_dataset.py` | raw rows → analysis-ready CSV |
| `code/extract_rules.py` | rule-based extraction of format/platform/focus |
| `code/verify_sources.py` | live URL + verbatim-quote verification |
| `code/validation.py` | agreement and kappa statistics |
| `code/analysis.py`, `code/charts.py` | summary statistics and figures |
| `notebooks/01_build_dataset.ipynb` | builds the CSV |
| `notebooks/02_validation.ipynb` | reproduces the agreement figures |
| `notebooks/03_analysis.ipynb` | reproduces the report figures |
| `figures/fig1–fig4` | figures used in the report |

## Field definitions
- `interview_status`: Required / Invitation only / No interview / **Not stated**. "Not stated" means no official or public page settles the question; it is never treated as "no interview".
- `has_interview`: 1 for Required or Invitation only.
- `interview_documented`: 1 if any statement exists (including an explicit "no interview").
- `format_primary`: Asynchronous video / Live 1:1 / Panel / Group / Test / Video + written / None / Unknown.
- `platform`: Kira Talent / Zoom/Teams/Skype / School platform / Telephone / In person / Not stated.
- `duration_min`: stated interview length in minutes (midpoint of ranges); blank if not stated.
- `question_count`: stated number of questions; blank if not stated.
- `q_*`: 1 if the source states the interview assesses that dimension.
- `example_questions`: verbatim questions from the cited page, separated by ` | `.
- `verified_url`, `verified_quote`: whether the URL returned content and the quote matched the retrieved page in the October audit.
- `evidence_type`, `confidence`: official / third_party / none; high / medium / low.

## Known gaps and biases
1. **Silence is the norm.** 85/150 programmes have no statement about interviews. The sample cannot distinguish "no interview" from "undisclosed interview".
2. **Format is thin.** 37 of the 60 interviewing programmes state a format; only 11 state a duration, 6 a question count, 11 any example question.
3. **Third-party evidence is uneven.** 17 interview records rest on public interview accounts, concentrated in Hong Kong and the US and dated 2020–2025; UK accounts rarely named the programme.
4. **Purposive sample.** Programmes were selected because they are relevant to WKU applicants, not randomly; regional shares are descriptive, not population estimates. Australia (17) and Singapore (9)/Macao (4) are small.
5. **Renames.** Several programmes changed names during 2025–26 (e.g. Northwestern MSiA → MLDS; Imperial → MSc Business Analytics & AI). Rows use the name on the page at collection.
6. **Coder reliability.** Format coding has low inter-coder agreement (κ = 0.12); format shares are exploratory. Prevalence is the robust variable (κ = 0.57).

## Reproduce
Run Jupyter from the project root:
```
jupyter nbconvert --to notebook --execute A2_repository/notebooks/01_build_dataset.ipynb
jupyter nbconvert --to notebook --execute A2_repository/notebooks/02_validation.ipynb
jupyter nbconvert --to notebook --execute A2_repository/notebooks/03_analysis.ipynb
```
The notebooks use only the Python standard library plus Pillow (for figures); no network access is needed to reproduce the analysis. Re-running `code/verify_sources.py` against the live web requires network access.

**Validation note.** The automated-vs-hand figures in Table 2 of the report are reproduced by `notebooks/02_validation.ipynb`, which reads the page texts captured at collection time from `work/pages/*.txt` (plus the `_evidence.txt` files). Those files are part of the collection evidence; commit the `work/pages/` directory alongside this repository so that the validation notebook reproduces the exact figures in the report. If the directory is absent, the notebook still runs but the automated-extraction figures change (recall drops to 17/65), so the committed `work/pages/` directory is required for a faithful reproduction.

## AI use
See `docs/AI_USE_LOG.md`. AI was used for retrieval assistance, code, the blind second coding pass, and drafting; every retained row carries a URL and a verbatim quote, and unverifiable rows were replaced rather than filled.
