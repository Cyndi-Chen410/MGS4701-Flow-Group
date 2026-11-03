import csv, re, os, json, random, sys
sys.path.insert(0,'A2_repository/code')
from extract_rules import fmt as rfmt, platform as rplat
from collections import Counter

def kappa(a, b):
    n=len(a); po=sum(x==y for x,y in zip(a,b))/n
    ca=Counter(a); cb=Counter(b)
    pe=sum(ca[k]*cb.get(k,0) for k in ca)/n/n
    return (po-pe)/(1-pe) if pe<1 else 1.0, po

def boot_ci(a,b,reps=2000):
    random.seed(11); vals=[]
    n=len(a)
    for _ in range(reps):
        idx=[random.randrange(n) for _ in range(n)]
        k,_=kappa([a[i] for i in idx],[b[i] for i in idx]); vals.append(k)
    vals.sort(); return vals[int(.025*reps)], vals[int(.975*reps)]

def interview_sents(text):
    s=[re.sub(r'\s+',' ',m.group(0)).strip() for m in re.finditer(r'[^.]{0,160}\binterview[^.]{0,200}\.',text,re.I)]
    return ' '.join(x for x in s if 30<len(x)<400)

def main():
    rows=list(csv.DictReader(open('A2_repository/data/interview_programs_150.csv',encoding='utf-8-sig')))
    data=[]
    for r in rows:
        i=r['id']; p=f'work/pages/{i}.txt'
        t=open(p,encoding='utf-8',errors='ignore').read() if os.path.exists(p) else ''
        pe=f'work/pages/{i}_evidence.txt'
        if os.path.exists(pe):
            t=(t+' '+open(pe,encoding='utf-8',errors='ignore').read())[:400000]
        sents=interview_sents(t)
        if r.get('evidence_quote'):
            sents=(r['evidence_quote']+' '+sents).strip()
        low=sents.lower()
        admission = bool(re.search(r'(admission interview|interview.{0,40}admission|invited to (an )?interview|interview stage|interview process|interviewed|attend an interview|no interview)', low))
        no_int = bool(re.search(r'no interview|not required to attend an interview|without an interview', low))
        auto_doc = 1 if (admission or no_int) else 0
        auto_fmt, auto_all = rfmt(sents)
        auto_plat = rplat(sents)
        data.append({'id':r['id'],'region':r['region_short'],'hand_doc':int(r['interview_documented']),
                     'auto_doc':auto_doc,'hand_fmt':r['format_primary'],'auto_fmt':auto_fmt,
                     'hand_plat':r['platform'],'auto_plat':auto_plat,'sents':sents})
    res={}
    # documented binary
    a=[d['hand_doc'] for d in data]; b=[d['auto_doc'] for d in data]
    k,po=kappa(a,b); lo,hi=boot_ci(a,b)
    res['documented']={'n':len(a),'accuracy':po,'kappa':k,'ci':[lo,hi],
        'tp':sum(1 for x,y in zip(a,b) if x==1 and y==1),'tn':sum(1 for x,y in zip(a,b) if x==0 and y==0),
        'fp':sum(1 for x,y in zip(a,b) if x==0 and y==1),'fn':sum(1 for x,y in zip(a,b) if x==1 and y==0)}
    # format on hand-stated formats
    sub=[d for d in data if d['hand_fmt'] not in ('Unknown','None')]
    a=[d['hand_fmt'] for d in sub]; b=[d['auto_fmt'] for d in sub]
    k,po=kappa(a,b); lo,hi=boot_ci(a,b)
    res['format']={'n':len(sub),'accuracy':po,'kappa':k,'ci':[lo,hi],
                   'table':{x:{y:sum(1 for p,q in zip(a,b) if p==x and q==y) for y in set(b)} for x in set(a)}}
    # platform on hand-stated platforms
    sub2=[d for d in data if d['hand_plat'] not in ('Not stated','')]
    a=[d['hand_plat'] for d in sub2]; b=[d['auto_plat'] for d in sub2]
    k,po=kappa(a,b); lo,hi=boot_ci(a,b)
    res['platform']={'n':len(sub2),'accuracy':po,'kappa':k,'ci':[lo,hi]}
    res['disagreements_doc']=[d for d in data if d['hand_doc']!=d['auto_doc']][:12]
    res['disagreements_fmt']=[d for d in data if d['hand_fmt'] not in ('Unknown','None') and d['hand_fmt']!=d['auto_fmt']][:12]
    json.dump(res,open('work/validation_results.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(json.dumps({k:(v if k not in ('disagreements_doc','disagreements_fmt') else len(v)) for k,v in res.items()},indent=1,ensure_ascii=False))

if __name__=='__main__': main()
