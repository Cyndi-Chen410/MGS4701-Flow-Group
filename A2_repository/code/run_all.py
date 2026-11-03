"""Run the whole A2 pipeline from the project root:
    python A2_repository/code/run_all.py
Produces: data/interview_programs_150.csv, data/validation_results.json,
          figures/fig1-4.png, the Excel workbook and the Word report.
"""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ROOT = os.path.dirname(REPO)
os.chdir(ROOT)
sys.path.insert(0, os.path.join(REPO, 'code'))

from build_dataset import build
import json, validation, analysis as A

rows = json.load(open(os.path.join(REPO, 'data/raw_rows.json')))
checks = json.load(open(os.path.join(REPO, 'data/source_checks.json')))
out = build(rows, checks, os.path.join(REPO, 'data/interview_programs_150.csv'))
print(f'[1/5] dataset: {len(out)} rows')

validation.main()
print('[2/5] validation: data/validation_results.json')

data = A.load(os.path.join(REPO, 'data/interview_programs_150.csv'))
A.fig_prevalence(data, os.path.join(REPO, 'figures/fig1_prevalence.png'))
A.fig_format(data, os.path.join(REPO, 'figures/fig2_format.png'))
A.fig_focus(data, os.path.join(REPO, 'figures/fig3_focus.png'))
A.fig_disclosure(data, os.path.join(REPO, 'figures/fig4_disclosure.png'))
print('[3/5] figures: figures/fig1-4.png')

import make_xlsx
xlsx = 'BA_DS硕士面试数据收集表_150条.xlsx'
make_xlsx.make(os.path.join(REPO, 'data/interview_programs_150.csv'), xlsx)
make_xlsx.add_chinese_sheet(xlsx)
make_xlsx.add_extra(xlsx, None)
make_xlsx.add_validation_sheet(xlsx)
print('[4/5] workbook:', xlsx)

subprocess.run([sys.executable, os.path.join(REPO, 'code/make_report.py')], check=True)
print('[5/5] report: A2_Findings_Report_ShenZhehao.docx')
