from processing import College, soupify, cols, makeframe
import re
from bs4 import BeautifulSoup as bs

# the basics
cypress = College('Cypress College')

url = 'https://www.dvc.edu/communication/schedules/search.html'

soupify(url, vanilla=True, use_ssl=True)

def __update__departments():
    pass

def build_func(self):
    pass


# bind build func to class
cypress.bind(build_func)
