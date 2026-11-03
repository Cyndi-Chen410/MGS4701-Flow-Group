import csv, math, json, statistics
from collections import Counter, defaultdict
import sys
sys.path.insert(0,'A2_repository/code')
import charts

REGIONS = ['US','UK','HK','SG','AU','MO']
LABEL = {'US':'United States','UK':'United Kingdom','HK':'Hong Kong SAR','SG':'Singapore','AU':'Australia','MO':'Macao SAR'}

def wilson(k, n, z=1.96):
    if n == 0: return (0,0)
    p = k/n; d = 1 + z*z/n
    c = p + z*z/(2*n); s = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return ((c-s)/d, (c+s)/d)

def load(path='A2_repository/data/interview_programs_150.csv'):
    rows = list(csv.DictReader(open(path, encoding='utf-8-sig')))
    for r in rows:
        for k in ['id','has_interview','interview_documented','duration_min','question_count',
                  'q_motivation','q_behavioural','q_technical','q_case','q_ethics','q_written','q_self_intro']:
            r[k] = int(r[k]) if str(r[k]).strip().isdigit() else None
    return rows

def summarize(rows):
    N = len(rows); out = {}
    out['N'] = N
    out['schools'] = len(set(r['school'] for r in rows))
    out['has'] = sum(r['has_interview'] for r in rows)
    out['documented'] = sum(r['interview_documented'] for r in rows)
    out['not_required'] = sum(1 for r in rows if r['interview_status']=='No interview')
    out['third_party'] = sum(1 for r in rows if r['evidence_type']=='third_party' and r['has_interview'])
    out['by_region'] = {}
    for reg in REGIONS:
        sub = [r for r in rows if r['region_short']==reg]
        k = sum(r['has_interview'] for r in sub); n = len(sub); d = sum(r['interview_documented'] for r in sub)
        lo, hi = wilson(k, n)
        out['by_region'][reg] = {'n':n,'schools':len(set(r['school'] for r in sub)),'k':k,'pct':k/n if n else 0,
                                 'lo':lo,'hi':hi,'documented':d,'doc_pct':d/n if n else 0}
    return out

def fig_prevalence(rows, path):
    s = summarize(rows)['by_region']
    labels = [f"{reg}\n(n={s[reg]['n']})" for reg in REGIONS]
    vals = [s[reg]['pct']*100 for reg in REGIONS]
    los = [s[reg]['pct']*100 - s[reg]['lo']*100 for reg in REGIONS]
    his = [s[reg]['hi']*100 - s[reg]['pct']*100 for reg in REGIONS]
    charts.bar_ci(path, labels, vals, los, his, 'Share of programmes with an interview stage (%)',
                  'Interviews are documented for a minority of programmes', ymax=100, fmt='{:.0f}%',
                  note='Bars show observed share; whiskers are 95% Wilson intervals. "Interview stage" = required or invitation-only.')

def fig_format(rows, path):
    has = [r for r in rows if r['has_interview'] and r['format_primary'] not in ('Unknown','None')]
    order = ['Asynchronous video','Live 1:1','Panel','Group','Test','Video + written','None']
    cnt = Counter(r['format_primary'] for r in has)
    labels = [k for k in order if cnt.get(k)]
    vals = [100*cnt[k]/len(has) for k in labels]
    charts.hbar(path, labels, vals, 'Share of programmes with a stated format (%)',
                f'Format mix among the {len(has)} programmes that state a format', fmt='{:.0f}%', xmax=100,
                note=f'US accounts for {sum(1 for r in has if r["region_short"]=="US")} of {len(has)}; HK {sum(1 for r in has if r["region_short"]=="HK")}, UK {sum(1 for r in has if r["region_short"]=="UK")}.')
def fig_focus(rows, path):
    has = [r for r in rows if r['has_interview']]
    keys = [('q_behavioural','Behavioural / experience'),('q_technical','Technical / quantitative'),
            ('q_motivation','Motivation / fit'),('q_case','Case / business problem'),
            ('q_written','Written component'),('q_self_intro','Self-introduction'),('q_ethics','Ethics')]
    n = len(has)
    vals = [(l, 100*sum(r[k] for r in has)/n) for k,l in keys]
    vals.sort(key=lambda x: x[1], reverse=True)
    charts.hbar(path, [v[0] for v in vals], [v[1] for v in vals], 'Share of interviewed programmes (%)',
                'What interviews are documented to assess', fmt='{:.0f}%', xmax=35,
                note=f'n={n} programmes with a documented interview stage; multi-label.')

def fig_disclosure(rows, path):
    cats = REGIONS
    series = {'Official statement':[], 'Third-party only':[], 'No statement found':[]}
    for reg in cats:
        sub = [r for r in rows if r['region_short']==reg]; n=len(sub)
        off = sum(1 for r in sub if r['interview_documented'] and r['evidence_type']=='official')
        tp = sum(1 for r in sub if r['interview_documented'] and r['evidence_type']=='third_party')
        none = n-off-tp
        series['Official statement'].append(100*off/n)
        series['Third-party only'].append(100*tp/n)
        series['No statement found'].append(100*none/n)
    charts.stacked(path, cats, series, 'How interview information is documented, by region (%)',
                   note='Official = programme/admissions page; third-party = named public interview-experience or consultancy page.')

def numbers(rows):
    has=[r for r in rows if r['has_interview']]
    fmt=Counter(r['format_primary'] for r in has)
    plat=Counter(r['platform'] for r in has)
    durs=[r['duration_min'] for r in has if r['duration_min']]
    qs=[r['question_count'] for r in has if r['question_count']]
    doc_formats=sum(1 for r in has if r['format_primary']!='Unknown')
    return {'fmt':fmt,'plat':plat,'dur_n':len(durs),'dur_med':statistics.median(durs) if durs else None,
            'dur_range':(min(durs),max(durs)) if durs else None,'q_n':len(qs),'q_med':statistics.median(qs) if qs else None,
            'doc_formats':doc_formats,'has_n':len(has)}

if __name__=='__main__':
    rows=load()
    s=summarize(rows); n=numbers(rows)
    print(json.dumps({'summary':s,'numbers':{k:(dict(v) if isinstance(v,Counter) else v) for k,v in n.items()}},ensure_ascii=False,indent=1))
