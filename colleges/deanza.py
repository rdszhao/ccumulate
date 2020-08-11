from processing import College, soupify, makeframe
from types import MethodType
import re

de_anza = College('De Anza College')
de_anza.update_session('F2020')

def is_active(url):
    soup = soupify(url, 'td')
    if len(soup) < 4:
        return False, soup
    return True, soup

# url with department information
dept_url = 'https://www.deanza.edu/schedule/'

# regex for getting department information
dept_re = re.compile(r'([A-Z\W]+) - (.+)')

def __update_departments__(self):
    # get all relevant info from soup object by directory
    soup = soupify(self.url, 'option', to_text=True)[1:]

    departments = []
    for listing in soup:
        dcode, dname = dept_re.search(listing).groups()
        url = f'https://www.deanza.edu/schedule/listings.html?dept={dcode}&t={self.period}'
        active, soup_obj = is_active(url)
        if active:
            departments.append((dcode, dname, soup_obj))

    self.departments = departments

# course info extraction regex
crn_re = re.compile(r'[0-9]{4,}')
course_re = re.compile(r'(.+)View')
date_re = re.compile(r'[^a-zA-Z]')
fall2020 = '09/21/2020 - 12/11/2020'

def update_df(self):
    # update / get all active departments first
    self.__update_departments__()

    # legacy ordering
    ordering = ['Department', 'Course', 'Enrollment', 'Name', 'Days', 'Times', 'Delivery']

    # build dict from extracted data to compile into dataframe
    course_dict = {}
    for dcode, dname, soup in self.departments:
        subj_dict = {}
        i = 0
        while True:
            if crn_re.match(soup[i]):
                crn = soup[i]
                subj_dict.update({crn: []})
                i += 1
                try:
                    while not crn_re.match(soup[i]):
                        if soup[i] != 'OL' and soup[i] != '':
                            if 'View' in soup[i]:
                                name = course_re.match(soup[i])
                                if name:
                                    soup[i] = name.group(1)
                            subj_dict[crn].append(soup[i])

                        i += 1
                except IndexError:
                    break

        # filter and format information
        for crn in subj_dict.keys():
            subj_dict[crn] = subj_dict[crn][:8]
            subj_dict[crn][4] = date_re.sub('', subj_dict[crn][4])
            if not subj_dict[crn][4]:
                subj_dict[crn][4] = 'TBA'
            try:
                del subj_dict[crn][1], subj_dict[crn][5]
            except IndexError:
                pass
            if 'TBA' in subj_dict[crn][4]:
                subj_dict[crn][4] = 'TBA'
            subj_dict[crn].insert(0, dname)
            # zip into diction according to specific_cols to ready for dataframe
            subj_dict[crn] = dict(zip(ordering, subj_dict[crn]))

        course_dict.update(subj_dict)

    # build df
    self.df = makeframe(
        course_dict,
        custom_cols=ordering,
        loc_name='De Anza College',
        normalize=True,
        Session=fall2020
    )
    return self.df

de_anza.update_df = MethodType(update_df, de_anza)
