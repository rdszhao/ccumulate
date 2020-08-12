from processing import College, Soup
import re

# the basics
SBCC = College('Santa Barbara City College')
SBCC.session = 'F2020'
URL = 'https://banner.sbcc.edu/PROD/pw_pub_sched.p_search?term=202130'

# xpqths for selenium driver
PUSH = '/html/body/div/div[2]/form/div[2]/div[5]/div/button[1]'
ELEMENTS = [
    '/html/body/div/div[2]/form/div[2]/div[4]/div/label[2]',
    PUSH
]

# regex for department information
dept_Re = re.compile(r'([\w]+)\s+-\s+([\w]+)')


def __update_departments__():
    'builds department dict and passes dept and soup objects on to build func'
    base = Soup(URL, xpaths=ELEMENTS)
    soup = base.extract('h2')
    depts = {}
    for option in soup:
        dcode, dname = dept_Re.search(option).groups()
        depts.update({dcode: dname})

    return depts, base


def __build_func__(self):
    departments, soup = __update_departments__()

base = Soup(URL, xpaths=ELEMENTS)
soup = base.extract('h3')


# bind build func to instance
SBCC.bind(__build_func__)
