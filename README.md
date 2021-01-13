# Simple Python script to authenticate to the University of Arkansas's Blackboard and access the API

Follows the same authentication flow as logging in from a browser.  Fiddler was used to reverse engineer the requests and translate to Python.

# Requirements
* Compatible with Python 2.7+ and 3.x
* The only non-standard library required is `requests`:
```
pip install requests
```
  
# Usage
Edit main.py and fill in values for UARK_EMAIL and UARK_PASSWORD.  Alternatively, the script can be run directly with:
```
python main.py "<uark email address>" "<uark password>"
```
i.e.
```
python main.py "johndoe@uark.edu" "thisisprobablynotmyrealpassword"
```

# Examples
The file examples.py contains 3 examples of API usage: 
* Listing Courses
* Checking Course Grades
* Checking Course Content and Downloading Attachments

The script can be run the same way as above:
```
python examples.py "<uark email address>" "<uark password>"
```

# Blackboard API
[Blackboard REST API documentation](https://developer.blackboard.com/portal/displayApi) <br/>
[Blackboard Github](https://github.com/blackboard)

The paths from the documentation are combined with the UARK blackboard URL, for example: `https://learn.uark.edu/learn/api/public/v1/announcements`
If you are logged into Blackboard in a browser, some of the simple routes can be accessed.  More examples:

* [Course List](https://learn.uark.edu/learn/api/public/v3/courses)
* [View Calendar Items](https://learn.uark.edu/learn/api/public/v1/calendars/items)
* [Privacy Policy](https://learn.uark.edu/learn/api/public/v1/system/policies/privacy)

There is a lot of other things that can be done based on a user's level of access and currently enrolled courses.

# Why?
I wanted to get programmatic access to the Blackboard API to see if I could automate some things, like downloading course materials.
As far as I can tell, the only other way to get access to this API is by [creating a developer application](https://docs.blackboard.com/learn/rest/getting-started/registry) and having a UARK Blackboard system administrator [create a REST API integration](https://docs.blackboard.com/learn/rest/getting-started/rest-and-learn).  

# Notes
* Even with 2FA enabled on my account this script did not trigger any additional authentication steps, even when logging in from a different IP.
* This works as of January 2021 but any changes in either UARK's or Microsoft's authentication process could break the script.
* The content data seems incomplete and I couldn't figure out how to access some attachments that I know exist but weren't returned by the API.
