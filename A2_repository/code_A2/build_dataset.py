"""Build the analysis-ready dataset from researched rows + verification output."""
import json, re, csv, sys, datetime
sys.path.insert(0,'A2_repository/code')
from extract_rules import fmt as rule_fmt, platform as rule_platform, focus as rule_focus

REGION_SHORT = {'United States':'US','United Kingdom':'UK','Hong Kong SAR':'HK','Singapore':'SG','Australia':'AU','Macao SAR':'MO'}

def norm_format(s):
    s = (s or '').lower()
    tags = []
    if re.search(r'asynchron|kira|recorded|pre-?recorded|video interview|video assessment', s): tags.append('Asynchronous video')
    if re.search(r'group', s): tags.append('Group')
    if re.search(r'panel|two interviewers|2 interviewers', s): tags.append('Panel')
    if re.search(r'\blive\b|zoom|teams|skype|one-to-one|1:1|in person|face-to-face|telephone|phone', s): tags.append('Live 1:1')
    if re.search(r'written|essay', s): tags.append('Video + written')
    if re.search(r'\btest\b|coding test|machine test|written test|assessment day', s): tags.append('Test')
    if re.search(r'no interview|not required|without interview', s): tags.append('None')
    # primary: prefer async if both async and live, else live, group, test
    order = ['Asynchronous video','Live 1:1','Panel','Group','Video + written','Test','None']
    for o in order:
        if o in tags: return o, '; '.join(dict.fromkeys(tags))
    return 'Unknown',''

def norm_platform(s):
    s = (s or '').lower()
    if 'kira' in s: return 'Kira Talent'
    if re.search(r'zoom|teams|skype|webex', s): return 'Zoom/Teams/Skype'
    if 'phone' in s or 'telephone' in s: return 'Telephone'
    if 'in person' in s or 'on campus' in s or 'face-to-face' in s: return 'In person'
    if re.search(r'school|own platform|university platform|custom|portal|wepow|astronaut|lantern', s): return 'School platform'
    return 'Not stated'

def degree_type(program, school=''):
    p = (program or '').lower()
    if 'business analytics' in p or re.search(r'\bba\b', p): return 'BA'
    if 'data science' in p or 'data analytics' in p or 'analytics' in p: return 'DS'
    return 'ADJ'

def status_label(s):
    return {'required':'Required','invitation_only':'Invitation only','not_required':'No interview','not_stated':'Not stated'}.get(s,'Not stated')

def to_int(v):
    if isinstance(v,int): return v
    m = re.search(r'\d+', str(v or ''))
    return int(m.group()) if m else None

def build(rows, verif, out_csv):
    vmap = {v['id']:v for v in verif}
    out=[]
    for r in sorted(rows, key=lambda x:x['id']):
        v = vmap.get(r['id'], {})
        status = r.get('interview_status','not_stated')
        blob = ' '.join([r.get('format','') or '', r.get('evidence_quote','') or '', r.get('notes','') or ''])
        fmt, fmt_all = rule_fmt(blob) if status != 'not_stated' else ('Unknown','')
        if status == 'not_required': fmt, fmt_all = 'None',''
        if fmt == 'Unknown':
            fmt2, fmt_all2 = norm_format(r.get('format',''))
            if fmt2 != 'Unknown': fmt, fmt_all = fmt2, fmt_all2
        if status in ('required','invitation_only') and fmt == 'None':
            fmt, fmt_all = 'Unknown', ''
        if status in ('required','invitation_only') and fmt == 'Unknown':
            fmt = 'Unknown'
        if status == 'not_stated':
            fmt, fmt_all = 'Unknown',''
        has = 1 if status in ('required','invitation_only') else 0
        qt = r.get('question_types') or []
        if status not in ('required','invitation_only'):
            qt = []
        examples = [e.strip() for e in (r.get('example_questions') or []) if e.strip()] if status in ('required','invitation_only') else []
        conf = r.get('confidence','')
        # downgrade confidence when quote not found
        if v and not v.get('quote_found') and r.get('evidence_type') != 'none':
            conf = 'low'
        out.append({
            'id': r['id'],
            'region': r['region'],
            'region_short': REGION_SHORT.get(r['region'], r['region']),
            'school': r['school'],
            'program': r.get('program_official_name') or r.get('program',''),
            'degree_type': degree_type(r.get('program_official_name') or r.get('program','')),
            'official_url': r.get('official_url',''),
            'interview_status': status_label(status),
            'has_interview': has,
            'interview_documented': 0 if status == 'not_stated' else 1,
            'format_primary': fmt,
            'format_all': fmt_all,
            'platform': (norm_platform(r.get('platform','')) if norm_platform(r.get('platform','')) != 'Not stated' else rule_platform(blob)),
            'duration_min': to_int(r.get('duration_min')),
            'question_count': to_int(r.get('question_count')),
            'q_motivation': int('motivation' in qt or 'motivation' in rule_focus(blob)),
            'q_behavioural': int('behavioural' in qt or 'behavioural' in rule_focus(blob)),
            'q_technical': int('technical' in qt or 'technical' in rule_focus(blob)),
            'q_case': int('case' in qt or 'case' in rule_focus(blob)),
            'q_ethics': int('ethics' in qt or 'ethics' in rule_focus(blob)),
            'q_written': int('written' in qt or 'written' in rule_focus(blob)),
            'q_self_intro': int('self_intro' in qt or 'self_intro' in rule_focus(blob)),
            'example_questions': ' | '.join(examples),
            'evidence_url': r.get('evidence_url',''),
            'evidence_quote': (r.get('evidence_quote') or '').replace('\n',' '),
            'evidence_type': r.get('evidence_type','none'),
            'confidence': conf,
            'verified_url': int(bool(v.get('official_status') == 200)),
            'verified_quote': int(bool(v.get('quote_found'))),
            'collection_date': '2026-10-29',
            'notes': r.get('notes','')
        })
    cols = list(out[0].keys())
    with open(out_csv,'w',newline='',encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)
    return out

if __name__ == '__main__':
    rows = json.load(open(sys.argv[1])); verif = json.load(open(sys.argv[2]))
    out = build(rows, verif, sys.argv[3])
    print('rows', len(out))
