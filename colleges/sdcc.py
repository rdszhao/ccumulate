from processing import College, FULL_CATS
from pandas.io.json import json_normalize
import requests
import re

# campus names
sdcc = College('San Diego Community College District')
sdcc.city = 'San Diego City College'
sdcc.miramar = 'San Diego Miramar College'
sdcc.mesa = 'San Diego Mesa College'

DEPT_FILE = 'sdcc_depts.txt'

# regex for departments
cid_Re = re.compile(r'=\"(.+)\"\>(.+)<')

def __update_departments__():
    'load departments from txt file'
    # source departments
    with open(DEPT_FILE, 'r') as depts:
        file = depts.readlines()

    departments = {}
    for line in file:
        line = line.strip()
        dcode, dname = cid_Re.search(line).groups()
        departments.update({dcode: dname})

    return departments


def __college_Replace__(campus, self):
    'replace truncated names with full college names'
    if 'City' in campus:
        return self.city
    if 'Mesa' in campus:
        return self.mesa
    if 'Miramar' in campus:
        return self.miramar


def __dt_merge__(start, end):
    'concatenate start and end datetimes'
    if ':' in start or '/' in start:
        return f'{start} - {end}'
    return 'N/A'


def __dept_replace__(dcode, ddict):
    'function to source full department name from dpt dict'
    try:
        return ddict[dcode]
    except KeyError:
        return 'unidentified'


def __gsx_fmt__(cats):
    'strip gsx formatting'
    if type(cats) is str:
        return f'gsx${cats}.$t'
    elif type(cats) is list:
        return [f'gsx${cat}.$t' for cat in cats]
    else:
        return 'processing error'


# relevant categories
CATS = [
    'classnbr',
    'college',
    'subject',
    'coursename',
    'classdescr',
    'days',
    'starttime',
    'endtime',
    'startdate',
    'enddate',
    'location',
]
gsx_cats = __gsx_fmt__(CATS)

# source the json file of all classes
SRC = 'https://spreadsheets.google.com/feeds/list/1SXlmCfzg27fkrtJRZWhPnPGJ0jyWCimCMK3k3hZnj5Q/od6/public/values?alt=json'


def __build_func__(self):
    'build df from cleaned json then clean to spec'
    response = requests.get(SRC)
    raw = response.json()
    narrowed = raw['feed']['entry']

    # convert json dictionary to dataframe
    df = json_normalize(narrowed)

    # get departments
    depts = __update_departments__()

    # dataframe operations
    df = (
        df
        [gsx_cats]
        .rename(columns=dict(zip(gsx_cats, CATS)))
    )
    df = df[df['location'].str.contains('Online')]
    df['Location'] = df['college'].apply(__college_Replace__, args=(self,))
    df = (
        df
        .rename(columns={'classnbr': 'crn'})
        .set_index('crn')
    )

    df['Enrollment'] = 'Open'
    df['Times'] = df['starttime'].combine(df['endtime'], __dt_merge__)
    df['Session'] = df['startdate'].combine(df['enddate'], __dt_merge__)
    df['Department'] = df['subject'].apply(__dept_replace__, args=(depts,))
    df = df.drop(columns=['college', 'subject', 'starttime', 'endtime', 'startdate', 'enddate'])

    # rename and reorder as per cols
    rename_dict = {
        'coursename': 'Course',
        'classdescr': 'Name',
        'days': 'Days',
        'location': 'Delivery',
    }
    df = df.rename(columns=rename_dict)
    return df[FULL_CATS]


# bind build function
sdcc.bind(__build_func__)
