# Coding scheme (v2.0, October 2026)

Unit of observation: one taught master's programme (unique school + programme), six regions.

## Metadata
- `region`: United States / United Kingdom / Hong Kong SAR / Singapore / Australia / Macao SAR
- `degree_type`: BA (business analytics), DS (data science), ADJ (analytics-adjacent: fintech, statistics, information systems, AI)

## Interview status (`I`)
| code | label | rule |
|---|---|---|
| 1 | Required | Official admission page states every admitted applicant interviews, or an interview is a mandatory application stage |
| 2 | Invitation only | Official page states interview is by invitation / shortlisted candidates only |
| 3 | Not required | Official page states there is no interview, or interview is explicitly optional |
| 0 | Not stated | No official statement found; absence is **not** evidence of no interview |

## Format (`F`) — primary format, multi-label allowed in `format_all`
| code | label | rule |
|---|---|---|
| 1 | Live 1:1 | Real-time one-to-one interview (Zoom, phone, in person) |
| 2 | Panel | Two or more interviewers in real time |
| 3 | Group | Group discussion / group case |
| 4 | Asynchronous video | Pre-recorded video answers, no interviewer present (Kira, school platform) |
| 5 | Video + written | Asynchronous video with a written component |
| 6 | Test | Timed written / machine / coding test as a selection stage |
| 7 | None | No interview stage |
| 0 | Unknown | Format not stated |

## Platform (`P`)
1 Kira Talent; 2 Zoom/Teams/Skype; 3 school-owned platform; 4 telephone; 5 in person; 0 unknown/not stated.

## Assessment focus (`Q`) — multi-label 0/1
- `motivation` — why this programme/school/career, fit, goals
- `behavioural` — past experience, teamwork, leadership, challenge (STAR)
- `technical` — statistics, ML, programming, mathematics, case-free technical probing
- `case` — business case, data case, estimation, group case
- `ethics` — AI ethics, data ethics, privacy
- `written` — timed essay / written response
- `self_intro` — self-introduction / walk me through your CV

Coding rule: code a focus only when the retrieved page states that the interview assesses it, or when a verbatim question on the page belongs to it. Do not infer from the programme curriculum.

## Evidence
- `evidence_type`: official / third_party / none
- `confidence`: high (official statement + current cycle), medium (official statement undated), low (third-party only)
- `evidence_quote`: verbatim sentence(s) from the cited page, <=300 characters.
