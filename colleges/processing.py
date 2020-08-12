from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd


# COLLEGE STRUCT

class College:
    'class to host build func and export data'
    # current academic session
    session = None
    # pandas df with course information
    data = None
    # function sequence that builds df
    build_func = None

    def __init__(self, name):
        'basic, kombucha-drinking constructor'
        self.name = name

    def bind(self, new_build_func):
        'bind build function to each instance'
        self.build_func = new_build_func

    def build(self):
        'return build function and return df as well as updating c.data'
        self.data = self.build_func(self)
        return self.data


# SITE SCRAPER
# backend: selenium

# set selenium options
options = Options()
options.add_argument = '--window-size1920.1200'
DRIVER_PATH = '/Users/raymondzhao/Documents/Projects/toolkit/scraping/chromedriver'


def __driver__(url, xpaths=None, headless=True):
    'uses a url to start a selenium chromedriver, navigating with xpaths as needed'
    options.headless = headless
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    driver.get(url)
    if xpaths:
        try:
            for xpath in xpaths:
                driver.find_element_by_xpath(xpath).click()
        except TypeError as e:
            raise(e)
    return driver


class Driver:
    'wrapper for selenium chromedriver'

    def __init__(self, url, xpaths=None, headless=True, persist=True):
        'returns a driver using parameters passed to __driver__'
        self.driver = __driver__(url, xpaths, headless)
        self.source = self.driver.page_source


    def __navigate__(self, xpaths=None):
        'navigates webpage with driver given xpaths'
        if xpaths:
            try:
                for xpath in xpaths:
                    self.driver.find_element_by_xpath(xpath).click()
            except TypeError as e:
                raise(e)
            self.source = self.driver.page_source


    def stop(self):
        self.driver.quit()


class Soup:
    'interface for selenium scraper and beautiful soup'
    def __init__(self, url, xpaths=None, headless=True, persist=True):
        'returns bsoup object of driver source'
        self.url = url
        self.persist = persist
        self.headless = headless

        self.driver = Driver(url, xpaths, headless, persist)
        src = self.driver.source
        self.base =  bs(src, features='lxml')
        if not self.persist:
            self.driver.stop()


    def rebase(self, xpaths):
        'navigates and updates base given new xpaths'
        if not self.persist:
            self.driver = self.driver.__navigate__(self, xpaths)
            src = self.driver.page_source
            self.base =  bs(src, features='lxml')
        else:
            print('only rebase if persist enabled')


    def extract(self, *tags, to_text=True, normalize=True, **attributes):
        'get tags and attributes from soup base with option for text conversion'
        findings = self.base.find_all(*tags, **attributes)

        if to_text:
            findings = [result.get_text() for result in findings]
            if normalize:
                findings = list(filter(None, [element.strip() for element in findings]))

        return findings


# STORAGE UTILITIES
# pandas

# universal ordering for consolidation
COLS = ['Department', 'Course', 'Name', 'Days', 'Times', 'Session', 'Delivery', 'Enrollment']
FULL_CATS = COLS.copy()
FULL_CATS.insert(0, 'Location')


def makeframe(dict, custom_cols=None, loc_name=None, online_filter=False, normalize=False, **new_cols):
    'construct a df from a roughly-formatted dictionary'
    # adhere to cols ordering if none specified
    if not custom_cols:
        custom_cols = COLS
    # build process
    df = pd.DataFrame().from_dict(
        dict,
        orient='index',
        columns=custom_cols
    )
    # optional: assign new columns
    if len(new_cols) > 0:
        df = df.assign(**new_cols)
    # filter out classes that aren't online
    if online_filter:
        df = df[df['Delivery'].str.contains('online', case=False)]
    # reorder according to COLS
    if normalize:
        df = df[COLS]
    # add singular location name
    if loc_name:
        df.insert(0, 'Location', loc_name)
    return df


def framecheck(df):
    'sanity checker'
    for cat in FULL_CATS:
        print(df[cat].iloc[0])
