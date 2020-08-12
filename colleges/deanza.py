from processing import College, __soupify__, __makeframe__
import re

de_anza = College('De Anza College')
de_anza.change_session('F2020')


def __is_active__(url):
    soup = __soupify__(url, 'td')
    if len(soup) < 4:
        return False, soup
    return True, soup


# url with department information
DEPT_URL = 'https://www.deanza.edu/schedule/'

# regex for getting department information
dept_Re = re.compile(r'([A-Z\W]+) - (.+)')


def __update_departments__(session):
    # get all relevant info from soup object by directory
    soup = __soupify__(DEPT_URL, 'option', to_text=True)[1:]

    departments = []
    for listing in soup:
        dcode, dname = dept_Re.search(listing).groups()
        url = f'https://www.deanza.edu/schedule/listings.html?dept={dcode}&t={session}'
        active, soup_obj = __is_active__(url)
        if active:
            departments.append((dcode, dname, soup_obj))

    return departments


# course info extraction regex
crn_Re = re.compile(r'[0-9]{4,}')
course_Re = re.compile(r'(.+)View')
date_Re = re.compile(r'[^a-zA-Z]')
FALL_2020 = '09/21/2020 - 12/11/2020'

# legacy ordering
ORDERING = ['Department', 'Course', 'Enrollment', 'Name', 'Days', 'Times', 'Delivery']


# uses departments to construct a df
def build_func(self):
    # update / get all active departments
    departments = __update_departments__(self.session)

    # build dict from extracted data
    course_dict = {}
    for dcode, dname, soup in departments:
        subj_dict = {}
        i = 0
        while True:
            if crn_Re.match(soup[i]):
                crn = soup[i]
                subj_dict.update({crn: []})
                i += 1
                try:
                    while not crn_Re.match(soup[i]):
                        if soup[i] != 'OL' and soup[i] != '':
                            if 'View' in soup[i]:
                                name = course_Re.match(soup[i])
                                if name:
                                    soup[i] = name.group(1)
                            subj_dict[crn].append(soup[i])

                        i += 1
                except IndexError:
                    break

        # filter and format information
        for crn in subj_dict.keys():
            subj_dict[crn] = subj_dict[crn][:8]
            subj_dict[crn][4] = date_Re.sub('', subj_dict[crn][4])
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
            subj_dict[crn] = dict(zip(ORDERING, subj_dict[crn]))

        course_dict.update(subj_dict)

    # build df
    df = __makeframe__(
        course_dict,
        custom_cols=ORDERING,
        loc_name=self.name,
        normalize=True,
        online_filter=True,
        Session=FALL_2020
    )
    return df


# bind the new build function to class
de_anza.bind(build_func)
