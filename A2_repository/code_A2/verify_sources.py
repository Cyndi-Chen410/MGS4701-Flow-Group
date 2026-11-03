"""Verify every row against the live page: URL status, programme identity, quote presence."""
import json, re, html, ssl, sys, os, time, urllib.request, concurrent.futures

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
PAGES = 'work/pages'
os.makedirs(PAGES, exist_ok=True)

def fetch(url):
    if not url or not url.startswith('http'):
        return 0, url, 'no url'
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})
    try:
        with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
            raw = r.read(2500000)
            cs = r.headers.get_content_charset() or 'utf-8'
            return r.status, r.geturl(), raw.decode(cs, 'ignore')
    except Exception as e:
        return 0, url, str(e)[:150]

def jina(url):
    try:
        req = urllib.request.Request('https://r.jina.ai/' + url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            return r.status, r.read(1500000).decode('utf-8', 'ignore')
    except Exception as e:
        return 0, str(e)[:120]

def clean(h):
    h = re.sub(r'(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', h)
    t = re.sub(r'(?s)<[^>]+>', ' ', h)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()

def norm(s):
    s = s.lower()
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('–', '-').replace('—', '-')
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def identity(text, row):
    t = norm(text)
    prog = [w for w in re.findall(r'[a-z]+', norm(row.get('program_official_name',''))) if len(w) > 3 and w not in {'master','science','business','analytics','data','degree','program','programme','with','and','the'}]
    return sum(1 for w in set(prog) if w in t)

def one(row):
    rec = {'id': row['id']}
    if not row.get('official_url'):
        rec.update({'official_status':0,'official_final_url':'','official_len':0,'program_tokens_found':0,'evidence_status':0,'quote_len':0,'quote_found':False})
        return rec
    st, fin, h = fetch(row['official_url'])
    rec['official_status'] = st
    rec['official_final_url'] = fin
    text = clean(h) if st else ''
    if st != 200 or len(text) < 1200:
        js, jt = jina(row['official_url'])
        if js == 200 and len(jt) > len(text):
            text = re.sub(r'\s+', ' ', jt)
            rec['via'] = 'jina'
    rec['official_len'] = len(text)
    rec['program_tokens_found'] = identity(text, row) if st else 0
    open(f'{PAGES}/{row["id"]}.txt', 'w', encoding='utf-8').write(text)
    ev = row.get('evidence_url') or ''
    if ev and ev != row['official_url']:
        st2, fin2, h2 = fetch(ev)
        rec['evidence_status'] = st2
        etext = clean(h2) if st2 else ''
        if st2 != 200 or len(etext) < 800:
            js, jt = jina(ev)
            if js == 200 and len(jt) > len(etext):
                etext = re.sub(r'\s+', ' ', jt)
        open(f'{PAGES}/{row["id"]}_evidence.txt', 'w', encoding='utf-8').write(etext)
    else:
        rec['evidence_status'] = st
        etext = text
    q = norm(row.get('evidence_quote',''))
    rec['quote_len'] = len(q)
    rec['quote_found'] = bool(q) and (q in norm(etext) or (len(q) > 60 and norm(etext).find(q[:60]) >= 0))
    return rec

if __name__ == '__main__':
    rows = json.load(open(sys.argv[1]))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        out = list(ex.map(one, rows))
    json.dump(out, open('work/verification.json','w'), ensure_ascii=False, indent=1)
    for r in out:
        print(r['id'], r['official_status'], r['program_tokens_found'], r.get('evidence_status'), r['quote_found'], r['quote_len'])
