from framework import full_cats
from pandas.io.json import json_normalize
import requests
import re

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

# campus names
sdcc_name = 'San Diego City College'
sdcc_miramar = 'San Diego Miramar College'
sdcc_mesa = 'San Diego Mesa College'

# source the json file of all classes
src = 'https://spreadsheets.google.com/feeds/list/1SXlmCfzg27fkrtJRZWhPnPGJ0jyWCimCMK3k3hZnj5Q/od6/public/values?alt=json'
response = requests.get(src)
raw = response.json()
narrowed = raw['feed']['entry']

# convert json dictionary to dataframe
df = json_normalize(narrowed)

def gsx_fmt(cats):
    if type(cats) is str:
        return f'gsx${cats}.$t'
    elif type(cats) is list:
        return [f'gsx${cat}.$t' for cat in cats]
    else:
        return 'processing error'

# make gsx formatting friendlier
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

# replace truncated names with full college names
def college_replace(campus):
    if 'City' in campus:
        return sdcc_name
    if 'Mesa' in campus:
        return sdcc_mesa
    if 'Miramar' in campus:
        return sdcc_miramar

# concatenate start and end datetimes
def dt_merge(start, end):
    if ':' in start or '/' in start:
        return f'{start} - {end}'
    return 'N/A'

# function to source full department name from dpt dict
def dpt_replace(dcode):
    try:
        return departments[dcode]
    except KeyError:
        return 'unidentified'

# dataframe operations
df = (
    df
    [gsx_cats]
    .rename(columns=dict(zip(gsx_cats, cats)))
)
df = df[df['location'].str.contains('Online')]
df['Location'] = df['college'].apply(college_replace)
df = (
    df
    .rename(columns={'classnbr': 'crn'})
    .set_index('crn')
)

df['Enrollment'] = 'Open'
df['Times'] = df['starttime'].combine(df['endtime'], dt_merge)
df['Session'] = df['startdate'].combine(df['enddate'], dt_merge)
df['Department'] = df['subject'].apply(dpt_replace)
df = df.drop(columns=['college', 'subject', 'starttime', 'endtime', 'startdate', 'enddate'])

# rename and reorder as per cols
rename_dict = {
    'coursename': 'Course',
    'classdescr': 'Name',
    'days': 'Days',
    'location': 'Delivery',
}
df = df.rename(columns=rename_dict)
df = df[full_cats]
