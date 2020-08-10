from framework import soupify, makeframe
import re

deanza_url = 'https://www.deanza.edu/schedule/'
deanza = soupify(deanza_url, vanilla=True)
searches = deanza.find_all('option')[1:]
course_id = re.compile(r'([A-Z\W]+) - (.+)')

def is_active(url):
    soup = soupify(url, 'td')
    if len(soup) < 4:
        return False, soup
    return True, soup

classes = []
for listing in searches:
    match = course_id.search(listing.get_text())
    cid, name = match.group(1), match.group(2)
    url = f'https://www.deanza.edu/schedule/listings.html?dept={cid}&t=F2020'
    active, soup_obj = is_active(url)
    if active:
        classes.append((cid, name, soup_obj))

deanza = 'De Anza College'

crn_re = re.compile(r'[0-9]{4,}')
course_re = re.compile(r'(.+)View')
date_re = re.compile(r'[^a-zA-Z]')
fall2020 = '09/21/2020 - 12/11/2020'

specific_cols = ['Department', 'Course', 'Enrollment', 'Name', 'Days', 'Times', 'Delivery']

master_dict = {}
for cid, cname, subj in classes:
    subj_dict = {}
    i = 0
    while True:
        if crn_re.match(subj[i]):
            crn = subj[i]
            subj_dict.update({crn: []})
            i += 1
            try:
                while not crn_re.match(subj[i]):
                    if subj[i] != 'OL' and subj[i] != '':
                        if 'View' in subj[i]:
                            name = course_re.match(subj[i])
                            if name:
                                subj[i] = name.group(1)
                        subj_dict[crn].append(subj[i])

                    i += 1
            except IndexError:
                break

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
        subj_dict[crn].insert(0, cname)
        subj_dict[crn] = dict(zip(specific_cols, subj_dict[crn]))

    master_dict.update(subj_dict)

df = makeframe(
    master_dict,
    custom_cols=specific_cols,
    loc_name=deanza,
    normalize=True,
    Session=fall2020
)
