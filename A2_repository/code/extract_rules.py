"""Rule-based extraction of interview attributes from page evidence text.
Used for (a) filling the dataset where the researcher left the field blank and
(b) the automated-extraction arm of the validation study."""
import re

def fmt(text):
    t = (text or '').lower()
    tags = []
    if re.search(r'kira|asynchronous|asynchron|recorded video|pre-?recorded|one-way|video essay|video assessment|video interview platform|record and submit', t):
        tags.append('Asynchronous video')
    if re.search(r'\bgroup\b|group discussion|group case', t):
        tags.append('Group')
    if re.search(r'\bpanel\b|two interviewers|three interviewers|panel interview', t):
        tags.append('Panel')
    if re.search(r'\blive\b|zoom|teams|skype|one-to-one|1:1|one on one|face-to-face|in person|on campus|telephone|phone interview|virtual interview|online interview|video-conference', t):
        tags.append('Live 1:1')
    if re.search(r'written (question|essay|component|exercise)|timed essay|essay question', t):
        tags.append('Video + written')
    if re.search(r'\btest\b|coding test|programming assessment|written exam|machine test|aptitude test|assessment day', t):
        tags.append('Test')
    if re.search(r'no interview|not required to attend an interview|without an interview', t):
        tags.append('None')
    order = ['Asynchronous video','Panel','Group','Live 1:1','Video + written','Test','None']
    for o in order:
        if o in tags:
            return o, '; '.join(dict.fromkeys(tags))
    if re.search(r'interview', t):
        return 'Unknown', ''
    return 'Unknown', ''

def platform(text):
    t = (text or '').lower()
    if 'kira' in t: return 'Kira Talent'
    if re.search(r'zoom|teams|skype|webex|video-conference', t): return 'Zoom/Teams/Skype'
    if re.search(r'telephone|phone interview', t): return 'Telephone'
    if re.search(r'in person|on campus|on-campus', t): return 'In person'
    if re.search(r'school platform|video interview platform|own platform|application portal|university platform|wepow|astronaut', t): return 'School platform'
    return 'Not stated'

def focus(text):
    t = (text or '').lower()
    out = set()
    if re.search(r'motivation|why (this|our|the) (programme|program|school)|career (goal|plan)|fit with|interest in the program', t): out.add('motivation')
    if re.search(r'behaviou?ral|leadership|teamwork|team work|challenge|experience|star|accomplishment', t): out.add('behavioural')
    if re.search(r'technical|statistic|probability|programming|python|machine learning|\bmath', t): out.add('technical')
    if re.search(r'\bcase\b|case study|business case|case interview', t): out.add('case')
    if re.search(r'ethic|privacy|responsible ai', t): out.add('ethics')
    if re.search(r'written (question|essay|component|exercise)|timed essay|essay question', t): out.add('written')
    if re.search(r'self-intro|introduce yourself|tell me about yourself|walk (me )?through your (resume|cv)', t): out.add('self_intro')
    return out

if __name__ == '__main__':
    print(fmt('Kira Talent video interview, 6 oral questions plus 1 written question (5 minutes)'))
