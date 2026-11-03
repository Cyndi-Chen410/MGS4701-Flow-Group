# AI use log (A1 + A2)

**Tool.** Claude, through a coding agent (DeepSeek Harness), October 2026.

| Stage | What the AI did | Human check |
|---|---|---|
| A1 pilot | Drafted the brief and cleaning code; the AI did not collect the 100 rows | Team collected rows manually |
| A2 audit | Ran a script against the 100 A1 URLs; counted dead links, generic pages and duplicate templates | Author reviewed the audit output |
| A2 collection | Retrieved official pages and public interview accounts; proposed rows with verbatim quotes and URLs | Every row required a URL and quote; 148/150 URLs re-checked; unverifiable rows replaced, not filled |
| A2 coding | Applied codebook v2.0; served as the blind second coder (Section 3.2) | First coder = author; disagreements analysed |
| A2 analysis | Wrote cleaning, extraction, validation and charting code | Author reviewed outputs against the raw rows |
| A2 writing | Drafted and edited the report | Author verified every number against the CSV |

**Limits.** The AI second coder is not a human coder: the κ in Section 3.2 measures codebook clarity and the adequacy of the evidence packet, not human–human reliability. A human second coder should replace it before final submission. AI was not used to invent rows, quotes or questions; where no source could be retrieved the row was coded "Not stated".
