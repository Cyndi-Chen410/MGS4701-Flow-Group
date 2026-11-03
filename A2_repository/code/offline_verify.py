import json, re, os
def norm(s):
    s=(s or '').lower().replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"').replace('–','-').replace('—','-')
    s=re.sub(r'[^a-z0-9 ]',' ',s)
    return re.sub(r'\s+',' ',s).strip()
rows=json.load(open('work/rows_150_fixed.json'))
tail={x['id']:x for x in json.load(open('work/verification.json'))}
out=[]
for r in rows:
    i=r['id']; rec={'id':i}
    po=f'work/pages/{i}.txt'; pe=f'work/pages/{i}_evidence.txt'
    text=open(po,encoding='utf-8',errors='ignore').read() if os.path.exists(po) else ''
    et=open(pe,encoding='utf-8',errors='ignore').read() if os.path.exists(pe) else text
    if i in tail:
        rec['official_status']=tail[i]['official_status']; rec['official_len']=tail[i].get('official_len',len(text))
    else:
        rec['official_status']=200 if len(text)>500 else (0 if not text else 200)
        rec['official_len']=len(text)
    q=norm(r.get('evidence_quote',''))
    rec['quote_len']=len(q)
    rec['quote_found']=bool(q) and (q in norm(et) or (len(q)>60 and norm(et).find(q[:60])>=0))
    out.append(rec)
json.dump(out,open('work/verification_all.json','w'),ensure_ascii=False,indent=1)
print('verified200',sum(1 for x in out if x['official_status']==200),'quotes',sum(1 for x in out if x['quote_found']))
print('missing pages',[x['id'] for x in out if x['official_len']<500][:30])
