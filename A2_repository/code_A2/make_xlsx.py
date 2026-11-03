import csv, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def make(csv_path, out_path):
    rows = list(csv.DictReader(open(csv_path, encoding='utf-8-sig')))
    wb = Workbook(); ws = wb.active; ws.title = 'Dataset (150)'
    headers = list(rows[0].keys())
    ws.append(headers)
    for r in rows: ws.append([r[h] for h in headers])
    head_fill = PatternFill('solid', fgColor='1F4E79')
    thin = Side(style='thin', color='D9DEE3')
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF', size=9)
        c.fill = head_fill; c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
    widths = {'id':5,'region':13,'region_short':7,'school':30,'program':38,'degree_type':7,'official_url':42,
              'interview_status':14,'has_interview':7,'interview_documented':9,'format_primary':16,'format_all':22,
              'platform':16,'duration_min':8,'question_count':9,'q_motivation':7,'q_behavioural':8,'q_technical':7,
              'q_case':6,'q_ethics':6,'q_written':7,'q_self_intro':7,'example_questions':50,'evidence_url':42,
              'evidence_quote':60,'evidence_type':9,'confidence':9,'verified_url':7,'verified_quote':7,'collection_date':10,'notes':35}
    for i, h in enumerate(headers, 1):
        ws.column_dimensions[get_column_letter(i)].width = widths.get(h, 14)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font = Font(size=9); c.alignment = Alignment(wrap_text=True, vertical='top')
            c.border = Border(bottom=thin)
    ws.freeze_panes = 'D2'; ws.auto_filter.ref = f'A1:{get_column_letter(len(headers))}{ws.max_row}'
    ws.row_dimensions[1].height = 34

    # Codebook sheet
    cb = wb.create_sheet('Codebook')
    cb.append(['Field', 'Definition / coding rule'])
    for a, b in [
        ('interview_status','Required / Invitation only / No interview / Not stated (absence of an official statement is not evidence of no interview)'),
        ('format_primary','Live 1:1; Panel; Group; Asynchronous video; Video + written; Test; None; Unknown'),
        ('platform','Kira Talent; Zoom/Teams/Skype; School platform; Telephone; In person; Not stated'),
        ('duration_min','Stated interview length in minutes (midpoint of a range); blank if not stated'),
        ('question_count','Number of questions stated on the source page; blank if not stated'),
        ('q_*','1 if the source states that the interview assesses this dimension, else 0'),
        ('evidence_quote','Verbatim sentence(s) from evidence_url, <=300 characters'),
        ('verified_url','1 if official_url returned HTTP 200 during the October 2026 audit'),
        ('verified_quote','1 if evidence_quote was found verbatim on the live page'),
    ]:
        cb.append([a, b])
    cb.column_dimensions['A'].width = 22; cb.column_dimensions['B'].width = 120
    for c in cb[1]:
        c.font = Font(bold=True, color='FFFFFF'); c.fill = head_fill
    for row in cb.iter_rows(min_row=2):
        row[0].font = Font(bold=True, size=9); row[1].font = Font(size=9)
        row[1].alignment = Alignment(wrap_text=True, vertical='top')
    wb.save(out_path)
    print('saved', out_path, len(rows), 'rows')

if __name__ == '__main__':
    make(sys.argv[1], sys.argv[2])

def add_extra(path, val):
    from openpyxl import load_workbook
    wb = load_workbook(path)
    ws = wb.create_sheet('A1 audit')
    ws.append(['A1 pilot audit (29 Oct 2026)', 'Result'])
    for a,b in [
        ('Rows in A1 pilot',100),('Source URLs',100),
        ('URLs returning a readable page',25),('Dead links (404/DNS/SSL)',18),('Blocked to automated access',57),
        ('Readable pages that mention an interview',3),('Readable pages that are generic programme pages',22),
        ('Rows sharing the identical duration string',22),('Rows sharing the identical three-question template',32),
        ('Rows outside the sampling frame (finance/accounting) or mis-specified',7)]:
        ws.append([a,b])
    ws.column_dimensions['A'].width=62; ws.column_dimensions['B'].width=16
    for c in ws[1]:
        c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='1F4E79')
    wb.save(path)

REG={'US':'美国','UK':'英国','HK':'中国香港','SG':'新加坡','AU':'澳大利亚','MO':'中国澳门'}
FMT={'Asynchronous video':'异步视频面试（录播/Kira类）','Live 1:1':'真人视频/线下一对一','Panel':'多对一/面板面试','Group':'群面','Test':'笔试/机试','Video + written':'录播视频+写作','None':'无面试','Unknown':'有面试但形式未说明'}
PLAT={'Kira Talent':'Kira Talent','Zoom/Teams/Skype':'Zoom/Teams/Skype','School platform':'院校自建平台','Telephone':'电话','In person':'线下','Not stated':'未说明'}
Q={'q_motivation':'动机','q_behavioural':'行为','q_technical':'技术','q_case':'案例','q_ethics':'伦理','q_written':'写作','q_self_intro':'自我介绍'}

def add_chinese_sheet(path):
    from openpyxl import load_workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    wb=load_workbook(path); ws=wb.create_sheet('中文表（150条）',1)
    heads=['序号','国家/地区','院校','项目名称','面试形式','面试平台','题目数量/时长','问题类型','典型面试问题示例','数据来源（可搜索验证）','来源类型','核验状态']
    ws.append(heads)
    rows=list(__import__('csv').DictReader(open('A2_repository/data/interview_programs_150.csv',encoding='utf-8-sig')))
    for r in rows:
        if r['interview_status']=='Not stated':
            form='官网未提及面试（不等于不面试）'
        elif r['interview_status']=='No interview':
            form='明确不要求面试'
        else:
            form=FMT.get(r['format_primary'],r['format_primary'])
        pl=PLAT.get(r['platform'],r['platform']) if r['has_interview']=='1' else ''
        dur=''
        if r['question_count']: dur+=f"{r['question_count']}题"
        if r['duration_min']: dur+=((' / ' if dur else '')+f"{r['duration_min']}分钟")
        qs='、'.join(v for k,v in Q.items() if r[k]=='1')
        src=r['evidence_url'] or r['official_url']
        st={'official':'院校官网','third_party':'第三方面经/公开页面','none':'院校官网（未提及面试）'}.get(r['evidence_type'],'')
        ver='链接可访问 + 引文已比对' if r['verified_quote']=='1' else ('链接可访问' if r['verified_url']=='1' else '未能自动核验')
        ws.append([int(r['id']),REG.get(r['region_short'],r['region']),r['school'],r['program'],form,pl or '—',dur or '—',qs or '—',
                   r['example_questions'].replace(' | ','\n') or '—',src or '—',st or '—',ver])
    widths=[6,11,32,40,28,18,14,22,55,48,16,20]
    for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w
    fill=PatternFill('solid',fgColor='1F4E79')
    for c in ws[1]:
        c.font=Font(bold=True,color='FFFFFF',size=9); c.fill=fill
        c.alignment=Alignment(wrap_text=True,vertical='center',horizontal='center')
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font=Font(size=9); c.alignment=Alignment(wrap_text=True,vertical='top')
    ws.freeze_panes='D2'; ws.auto_filter.ref=f'A1:L{ws.max_row}'
    wb.save(path)

def add_validation_sheet(path):
    import json
    from openpyxl import load_workbook
    from openpyxl.styles import Font, PatternFill
    wb = load_workbook(path); ws = wb.create_sheet('Validation')
    v = json.load(open('work/validation_results.json', encoding='utf-8'))
    ws.append(['Comparison','n','Agreement','Cohen kappa','95% CI low','95% CI high'])
    def add(name, d):
        ws.append([name, d['n'], round(d['accuracy'],3), round(d['kappa'],3), round(d['ci'][0],3), round(d['ci'][1],3)])
    add('Automated vs hand: interview documented', v['documented'])
    add('Automated vs hand: format', v['format'])
    add('Automated vs hand: platform', v['platform'])
    ws.append([])
    ws.append(['Inter-coder (Coder A vs blind Coder B)','n','Agreement','Cohen kappa','95% CI low','95% CI high'])
    for row in [('Interview documented (all)',150,0.800,0.571,0.448,0.693),
                ('Interview documented (records with text)',54,0.889,0.725,0.492,0.911),
                ('Format',37,0.189,0.123,0.041,0.215),
                ('Platform',31,0.097,0.076,0.000,0.159)]:
        ws.append(list(row))
    for c in ws[1] + ws[8]:
        c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F4E79')
    for col, w in zip('ABCDEF', [46, 8, 12, 14, 12, 12]):
        ws.column_dimensions[col].width = w
    wb.save(path)
