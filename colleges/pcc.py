from processing import College, __soupify__, __driver__
from selenium.webdriver import ActionChains
import re

# the basics
PCC = College('Pasadena City College')
DEPT_URL = 'https://banner.sbcc.edu/PROD/pw_pub_sched.p_search?term=202130'

driver = __driver__(DEPT_URL, headless=False)
searchbox = driver.find_element_by_xpath('/html/body/div/div[2]/form/div[2]/div[5]/div/button[1]')
searchbox.click()
searchbox
__soupify__(driver, vanilla=True)

def __update_departments__():
    soup = __soupify__(DEPT_URL, 'select', to_text=False)[2].find_all('option')[1:]

    depts = {}
    for option in soup:
        dcode = option['value']
        dname = option.get_text().replace('\n', '').strip()
        depts.update({dcode: dname})

    return depts
