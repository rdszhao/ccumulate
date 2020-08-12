from processing import College, soupify, extract, makeframe, COLS
import re

# the basics
lacc = College('LA City College')
lacc.session = 'Fall'

URL = f'https://www.lacitycollege.edu/Academics/Classes/Open-Classes-{lacc.session}'


# make index / dictionary of departments by acronym
def __update_departments__():
    'compile department dict'
    base = soupify(URL)
    depts = extract(base, 'div', to_text=False, class_='oneQuarterWidth openAnchorLink')
    depts = {subj.find_all('a')[0]['href'][1:]: subj.get_text() for subj in depts}
    return depts, base


# regex for parsing courses
name_Re = re.compile(r'(.+) ([0-9].+): (.+)')
crn_Re = re.compile(r'([0-9]+) ([\w]+)')
delivery_Re = re.compile(r'Location: (.+)')
dt_meeting_Re = re.compile(r'Class Meets:\s+([\w]+) from (.+)')
hr_meeting_Re = re.compile(r'Class Meets: (.+)')
date_Re = re.compile(r'Class Starts:\s+(.+)\s+Class Ends:\s+(.+)')


# build df from dictionary compiled from regex parsing
def __build_func__(self):
    'iterates down the page to compile dict, builds df from dict'
    depts, base = __update_departments__()
    soup = extract(base, 'div', class_='openClassItem clearfix')
    class_dict = {}
    for section in soup:
        course = list(filter(None, section.split('\n')))

        subj, sect, desc = name_Re.search(course[0]).groups()
        subj = subj.replace(' ', '')
        dept = depts[subj]
        crn, component = crn_Re.search(course[1]).groups()
        name = f'{subj} {sect} - {component}'
        delivery = delivery_Re.search(course[3]).group(1).strip()

        try:
            days, times = dt_meeting_Re.search(course[4]).groups()
        except AttributeError:
            try:
                times = hr_meeting_Re.search(course[4]).group(1).strip()
            except AttributeError:
                time = 'CHECK SITE'
            finally:
                days = 'CHECK SITE'

        start, end = date_Re.search(course[5]).groups()
        session = f'{start} - {end}'

        info = dict(zip(COLS, [dept, name, desc, days, times, session, delivery, 'OPEN']))
        class_dict.update({crn: info})

    # build df from dictionary
    df = makeframe(
        class_dict,
        loc_name=self.name,
        online_filter=True,
        normalize=True
    )
    return df


# bind build function
lacc.bind(__build_func__)
