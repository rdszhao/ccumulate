from framework import soupify, cols, makeframe
import re

# the basics
lacc_name = 'LA City College'
lacc_url = 'https://www.lacitycollege.edu/Academics/Classes/Open-Classes-Fall'
soup = soupify(lacc_url, 'div', use_ssl=True, class_='openClassItem clearfix')

# make index / dictionary of departments by acronym
long_depts = soupify(
    lacc_url,
    'div',
    use_ssl=True,
    to_text=False,
    class_='oneQuarterWidth openAnchorLink'
)
depts = {subj.find_all('a')[0]['href'][1:]: subj.get_text() for subj in long_depts}

# regex for parsing names
name_re = re.compile(r'(.+) ([0-9].+): (.+)')
crn_re = re.compile(r'([0-9]+) ([\w]+)')
delivery_re = re.compile(r'Location: (.+)')
dt_meeting_re = re.compile(r'Class Meets:\s+([\w]+) from (.+)')
hr_meeting_re = re.compile(r'Class Meets: (.+)')
date_re = re.compile(r'Class Starts:\s+(.+)\s+Class Ends:\s+(.+)')

# use regex compile classes into df-ready dictionary format
def merge_dates(start, end):
    return f'{start} - {end}'

class_dict = {}
for section in soup:
    course = list(filter(None, section.split('\n')))
    subj, sect, desc = name_re.search(course[0]).groups()
    subj = subj.replace(' ', '')
    dept = depts[subj]
    crn, component = crn_re.search(course[1]).groups()
    name = f'{subj} {sect} - {component}'
    delivery = delivery_re.search(course[3]).group(1).strip()
    try:
        days, times = dt_meeting_re.search(course[4]).groups()
    except AttributeError:
        try:
            times = hr_meeting_re.search(course[4]).group(1).strip()
        except AttributeError:
            time = 'CHECK SITE'
        finally:
            days = 'CHECK SITE'
    start, end = date_re.search(course[5]).groups()
    session = merge_dates(start, end)
    info = dict(zip(
        cols,
        [dept, name, desc, days, times, session, delivery, 'OPEN']
    ))
    class_dict.update({crn: info})

# build df from dictionary
df = makeframe(
    class_dict,
    loc_name=lacc_name,
    online_filter=True,
    normalize=True
)
