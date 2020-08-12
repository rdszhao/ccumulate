from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd

# class to host build func and export data
class College:
    session = None
    data = None
    build_func = None

    def __init__(self, name):
        self.name = name

    def change_session(self, new):
        self.session = new

    def bind(self, new_build_func):
        self.build_func = new_build_func

    def build(self):
        self.data = self.build_func(self)
        return self.data


# web scraping backend
options = Options()
options.headless = True
options.add_argument = '--window-siz1920.1200'
DRIVER_PATH = '/Users/raymondzhao/Documents/Projects/toolkit/scraping/chromedriver'

# returns a driver
def __driver__(url, headless=True):
    if not headless:
        options.headless = False
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    driver.get(url)
    return driver


# returns the page source of either a driver or a url
def __src_driver__(drv):
    src = drv
    if type(src) is str:
        drv = __driver__(src)
    src = drv.page_source
    drv.quit()
    return src


# returns bsoup object of driver source
def __soupify__(src, *tags, vanilla=False, to_text=True, **attributes):
    soup = bs(__src_driver__(src), 'lxml')
    if vanilla:
        return soup
    findings = soup.find_all(*tags, **attributes)
    if to_text:
        findings = [result.get_text() for result in findings]
    return findings


# unified ordering
COLS = ['Department', 'Course', 'Name', 'Days', 'Times', 'Session', 'Delivery', 'Enrollment']
FULL_CATS = COLS.copy()
FULL_CATS.insert(0, 'Location')


# construct a df from a roughly-formatted dictionary
def __makeframe__(dict, custom_cols=None, loc_name=None, online_filter=False, normalize=False, **new_cols):
    if not custom_cols:
        custom_cols = COLS
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


# sanity checker
def __framecheck__(df):
    for cat in FULL_CATS:
        print(df[cat].iloc[0])
