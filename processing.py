from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import pandas as pd
import ssl

def url_process(url, use_ssl=False):
    if use_ssl:
        raw = urlopen(url, context=ssl.SSLContext())
    else:
        raw = urlopen(url)
    return bs(raw, 'lxml')


def soupify(url, *tags, vanilla=False, use_ssl=False, to_text=True, **attributes):
    soup = url_process(url, use_ssl)
    if vanilla:
        return soup
    findings = soup.find_all(*tags, **attributes)
    if to_text:
        findings = [result.get_text() for result in findings]
    return findings


cols = ['Department', 'Course', 'Name', 'Days', 'Times', 'Session', 'Delivery', 'Enrollment']
full_cats = cols.copy()
full_cats.insert(0, 'Location')

def makeframe(dict, custom_cols=None, loc_name=None, online_filter=False, normalize=False, **new_cols):
    if not custom_cols:
        custom_cols = cols
    df = pd.DataFrame().from_dict(
        dict,
        orient='index',
        columns=custom_cols
    )
    if len(new_cols) > 0:
        df = df.assign(**new_cols)
    if online_filter:
        df = df[df['Delivery'].str.contains('online', case=False)]
    if normalize:
        df = df[cols]
    if loc_name:
        df.insert(0, 'Location', loc_name)
    return df

def framecheck(df):
    for cat in full_cats:
        print(df[cat].iloc[0])
