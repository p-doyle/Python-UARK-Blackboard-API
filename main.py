import requests
import json
import pprint
import sys

try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    # python 2.7 compatibility
    from urlparse import urlparse, parse_qs


UARK_EMAIL = '<your UARK email address>'
UARK_PASSWORD = '<your UARK password>'

UARK_BLACKBOARD_URL = 'https://learn.uark.edu'
MICROSOFT_LOGIN_URL = 'https://login.microsoftonline.com'

# if at least 2 command line arguments were provided assume they are the username and password
if len(sys.argv) > 2:
    UARK_EMAIL = sys.argv[1]
    UARK_PASSWORD = sys.argv[2]


def get_authed_session(username, password):

    # create a session so our cookies are saved
    s = requests.session()

    # the main login page
    r = s.get('{}/webapps/login/'.format(UARK_BLACKBOARD_URL))

    # there is a button on the page to the saml login that contains query string values that we need in the next request
    saml_login_url = r.text.split('<p class="button-uark"><a href="')[1].split('"')[0]

    # an id from the URL's query string is needed later when authing back to UARK's system
    # parse the url, then parse the url's query string, then turn the results into a dict
    uark_ap_id = dict(parse_qs(urlparse(saml_login_url).query))['apId'][0]

    # this will redirect to microsoft
    r = s.get(saml_login_url)

    # manually follow the redirect
    r = s.get(r.url, params={'sso_reload': 'true'})

    # there is a javascript dictionary included with the page that contains data used when submitting the login form
    # isolate the dictionary string from the response text and turn it into a dict obj
    page_dict = json.loads(r.text.split('$Config=')[1].split(';\n//]]')[0])

    # use the values from the dict to populate the body for the next request
    data = {
        # not required?
        # 'canary': page_param_dict['canary'],
        'ctx': page_dict['sCtx'],
        'flowToken': page_dict['sFT'],
        'hpgrequestid': page_dict['sessionId'],
        'login': username,
        'passwd': password
    }

    # the URL from the previous request contains a uuid used in the next one
    path_uuid = urlparse(r.url).path.split('/')[1]

    # post the login to microsoft
    r = s.post('{}/{}/login'.format(MICROSOFT_LOGIN_URL, path_uuid), data=data)

    # another js dict
    page_dict = json.loads(r.text.split('$Config=')[1].split(';\n//]]')[0])

    # more tokens to include in the next request
    data = {
        # 'canary': page_dict['canary'],
        'ctx': page_dict['sCtx'],
        'flowToken': page_dict['sFT'],
        'hpgrequestid': page_dict['sessionId']
    }

    # something to do with microsoft's 'keep me signed in' prompt
    r = s.post('{}/kmsi'.format(MICROSOFT_LOGIN_URL), data=data)

    # the kmsi prompt's confirmation button contains the SAML response needed to authenticate with the UARK system
    saml_response = r.text.split('SAMLResponse" value="')[1].split('"')[0]

    # send the SAMLResponse to UARK to complete authentication
    # the request response will contain a cookie that is the only thing needed to auth with the blackboard api
    s.post('{}/auth-saml/saml/SSO/alias/{}'.format(UARK_BLACKBOARD_URL, uark_ap_id),
           data={'SAMLResponse': saml_response})

    return s


# only run this if the script is called directly
if __name__ == '__main__':
    session = get_authed_session(UARK_EMAIL, UARK_PASSWORD)

    # now use the session to send a request to the Blackboard API to check the recent announcements
    r = session.get('{}/learn/api/public/v1/announcements'.format(UARK_BLACKBOARD_URL))
    pprint.pprint(r.json())

    # can also create a new request with just the auth cookie
    '''
    r = requests.get('{}/learn/api/public/v1/announcements'.format(UARK_BLACKBOARD_URL),
                     cookies={'BbRouter': s.cookies.get('BbRouter')})
    pprint.pprint(r.json())
    '''

