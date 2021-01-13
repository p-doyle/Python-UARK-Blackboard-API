import pprint
import requests
import json
import sys
from main import get_authed_session, UARK_BLACKBOARD_URL


UARK_EMAIL = '<your UARK email address>'
UARK_PASSWORD = '<your UARK password>'

# if at least 2 command line arguments were provided assume they are the username and password
if len(sys.argv) > 2:
    UARK_EMAIL = sys.argv[1]
    UARK_PASSWORD = sys.argv[2]

session = get_authed_session(UARK_EMAIL, UARK_PASSWORD)

# its possible to use the Blackboard API to search the Users to find our User Id but its much easier to
#  just pull it from the blackboard home page
r = session.get('{}/ultra'.format(UARK_BLACKBOARD_URL))

# once again there is a javascript dictionary on the page and it contains our user id
user_dict = json.loads(r.text.split('user: ')[1].split(',\n')[0])


'''
List Courses
'''
# get a list of courses, sorting by the date created so the most recent courses are listed first
r = session.get('{}/learn/api/public/v1/users/{}/courses'.format(UARK_BLACKBOARD_URL, user_dict['id']),
                params={'sort': 'created(desc)'})
pprint.pprint(r.json())

# the list doesn't have much details so to find out more we need to query each course individually
for course in r.json()['results']:
    r2 = session.get('{}/learn/api/public/v3/courses/{}'.format(UARK_BLACKBOARD_URL, course['courseId']))
    pprint.pprint(r2.json())

# select the most recent course, presumably it will be one you are enrolled in now
most_recent_course = r.json()['results'][1]

'''
Check Course Grades
'''
# check your grades for the class
r = session.get('{}/learn/api/public/v2/courses/{}/gradebook/users/{}'.format(UARK_BLACKBOARD_URL,
                                                                              most_recent_course['courseId'],
                                                                              user_dict['id']))
pprint.pprint(r.json())

# once again, the initial listing does not give much detail so we need to figure out what each grade was for
for entry in r.json()['results']:

    # columns are essentially just anything graded, i.e. Assignment #1, Midterm Exam, Final Letter Grade, etc
    r = session.get('{}/learn/api/public/v2/courses/{}/gradebook/columns/{}'.format(UARK_BLACKBOARD_URL, most_recent_course['courseId'],
                                                                                    entry['columnId']))
    pprint.pprint(r.json())


'''
Check Course Content and Download Attachments
'''
# the base course URL doesn't change so create a variable to avoid repetition
base_course_url = '{}/learn/api/public/v1/courses/{}/contents'.format(UARK_BLACKBOARD_URL,
                                                                      most_recent_course['courseId'])
# list the content for the course
r = session.get(base_course_url)
pprint.pprint(r.json())

for content in r.json()['results']:

    # for each piece of content, check to see if it has any children
    r2 = session.get('{}/{}/children'.format(base_course_url, content['id']))
    # in case the content doesn't have any children, use .get()
    for child in r2.json().get('results', []):

        # try to find any attachments for the child content
        r3 = session.get('{}/{}/attachments'.format(base_course_url, child['id']))
        pprint.pprint(r3.json())

        for attachment in r3.json().get('results', []):

            # download each attachment
            print('downloading {}'.format(attachment['fileName']))
            r3 = session.get('{}/{}/attachments/{}/download'.format(base_course_url, child['id'], attachment['id']))

            # and save it to the current working directory
            with open(attachment['fileName'], 'wb') as f:
                f.write(r3.content)


