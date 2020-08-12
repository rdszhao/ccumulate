from processing import College, __soupify__
import re

# the basics
PCC = College('Pasadena City College')
PCC.session = 'F2020'
URL = 'https://banner.sbcc.edu/PROD/pw_pub_sched.p_search?term=202130'


def __update_departments__():
    soup = __soupify__(URL, 'select', to_text=False)[2].find_all('option')[1:]
    depts = {}
    for option in soup:
        dcode = option['value']
        dname = option.get_text().replace('\n', '').strip()
        depts.update({dcode: dname})
    return depts


PUSH = '/html/body/div/div[2]/form/div[2]/div[5]/div/button[1]'
ELEMENTS = [
    '//*[@id="sel_attr"]/option[44]',
    '/html/body/div/div[2]/form/div[2]/div[4]/div/label[2]',
    PUSH
]

soup = __soupify__(URL, xpaths=ELEMENTS, to_text=True, debug=True)
soup
