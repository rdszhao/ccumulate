from processing import College, full_cats
from pandas.io.json import json_normalize
import requests
import re

# campus names
sdcc = College('San Diego Community College District')
sdcc.city = 'San Diego City College'
sdcc.miramar = 'San Diego Miramar College'
sdcc.mesa = 'San Diego Mesa College'

def __update_departments__():
    # source department / acro information
    with open('sdcc_depts.txt', 'r') as depts:
        file = depts.readlines()

    # regex for building department dictionary
    cid_re = re.compile(r'=\"(.+)\"\>(.+)<')

    departments = {}
    for line in file:
        line = line.strip()
        dcode, dname = cid_re.search(line).groups()
        departments.update({dcode: dname})

    return departments

# replace truncated names with full college names
def college_replace(campus, self):
    if 'City' in campus:
        return self.city
    if 'Mesa' in campus:
        return self.mesa
    if 'Miramar' in campus:
        return self.miramar

# concatenate start and end datetimes
def dt_merge(start, end):
    if ':' in start or '/' in start:
        return f'{start} - {end}'
    return 'N/A'

# function to source full department name from dpt dict
def dpt_replace(dcode, ddict):
    try:
        return ddict[dcode]
    except KeyError:
        return 'unidentified'

# strip gsx formatting
def gsx_fmt(cats):
    if type(cats) is str:
        return f'gsx${cats}.$t'
    elif type(cats) is list:
        return [f'gsx${cat}.$t' for cat in cats]
    else:
        return 'processing error'

# relevant categories
cats = [
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
gsx_cats = gsx_fmt(cats)

# source the json file of all classes
src = 'https://spreadsheets.google.com/feeds/list/1SXlmCfzg27fkrtJRZWhPnPGJ0jyWCimCMK3k3hZnj5Q/od6/public/values?alt=json'

def build_func(self):
    response = requests.get(src)
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
        .rename(columns=dict(zip(gsx_cats, cats)))
    )
    df = df[df['location'].str.contains('Online')]
    df['Location'] = df['college'].apply(college_replace, args=(self,))
    df = (
        df
        .rename(columns={'classnbr': 'crn'})
        .set_index('crn')
    )

    df['Enrollment'] = 'Open'
    df['Times'] = df['starttime'].combine(df['endtime'], dt_merge)
    df['Session'] = df['startdate'].combine(df['enddate'], dt_merge)
    df['Department'] = df['subject'].apply(dpt_replace, args=(depts,))
    df = df.drop(columns=['college', 'subject', 'starttime', 'endtime', 'startdate', 'enddate'])

    # rename and reorder as per cols
    rename_dict = {
        'coursename': 'Course',
        'classdescr': 'Name',
        'days': 'Days',
        'location': 'Delivery',
    }
    df = df.rename(columns=rename_dict)

    return df[full_cats]

# bind build func to instance
sdcc.bind(build_func)
df = sdcc.build()
