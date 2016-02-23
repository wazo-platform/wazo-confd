Xivo-confd integration tests
============================

This README attempts to document various bits of information pertaining to the integration tests for
this project.

Running tests
=============

Please read the README at the project's root

Writing tests
=============

URLs, Requests, Responses
-------------------------

The test framework offers a helper for building and sending requests to URLs without having to concatenate various
strings and variables haphazardly. URL building works by chaining together calls to the helper.

```python
from test_api import confd

url = confd.foo.bar.spam.eggs
print url # http://confd:9486/1.1/foo/bar/spam/eggs

# IDs and other variables can be inserted when building an URL
user_id = 10
url = confd.users(user_id).lines
print url # http://confd:9486/1.1/users/10/lines
```

A request can be sent by calling one of the HTTP methods on a url (```get()```,
```post()```, ```put()``` or ```delete()```). These methods accept optional arguments. When passed to
```get```, the arguments will be converted to query parameters. When passed to ```put``` or
```post```, they will be JSON encoded and embedded in the request's body.

```python
# GET http://confd:9486/users?search=John&limit=10
response = confd.users.get(search="John", limit=10)

# POST http://confd:9486/users {"firstname": "John", "lastname": "Smith"}
response = confd.users.post(firstname="John", lastname="Smith")
```

Every request returns a ```Response``` object. The response offers the following attributes

```python
#Returns the HTTP status code (200, 400, etc)
response.status

#Response content as a plain string
response.raw

#Converts the content from JSON to a dict
response.json

#Checks that the reponse has a valid status code (200, 201, 204) and returns the JSON dict
response.item

#Some requests return a 'list' response, formatted as a JSON object '{"total": 1, "items": [...]}'
# .items checks the status code and returns the 'items' key as a list
response.items

#Returns the total number of items in 'list' responses
response.total

#If a response contains CSV data, convert it into a list of dicts where each dict represents a row
response.csv()
```

The response also offers some methods that make common assertions easier to manage

```python
#Assert that the HTTP status code is equal to 200
response.assert_status(200)

#Assert that the HTTP status is one of 200, 201 or 204
response.assert_ok()

#Assert that the resposne contains a "Location:" header with a URL formatted for a given resource.
#i.e. Responses for users should have a header "Location: http://confd:9486/1.1/users"
response.assert_location('users')

#Assert that the JSON body contains a 'link' property that has a URL for a given resource.
#e.g.: {"id": 12, "links": [{"rel": "users", "href": "http://confd:9486/1.1/users/12"}]}
response.assert_link('users')

#Assert that the request has created a resource. A resource is considered created when it has
#the status code 201, contains a "Location" header, and contains a url for the created resource
#in the JSON body. The following example checks that a 'user' resource has been created.
response.assert_created('users')

#These 2 assertions make sure that PUT or DELETE requests return the status code 204
response.assert_updated()
response.assert_deleted()

#Assertion for checking error responses. First parameter is the expected status code.
#Second parameter is a regular expression for the expected error message
import re
expected_status_code = 400
expected_error_message = re.compile(r"Input Error - User already exists")

response.assert_match(expected_status_code, expected_error_message)
```

Test fixtures
-------------

Fixtures are a mechanism for creating resources that are needed for performing a test. They often
represent the preconditions of a test. Fixtures can be used as decorators or context managers.  When
used as a decorator, a dict of the resource that has been created will be passed to the test
function. Fixtures will destroy the resource at the end of the test.

```python
from test_api import fixtures
from test_api import confd

@fixtures.user()
@fixtures.line()
def test_association_between_user_and_line(user, line):
    url = confd.users(user['id']).lines
    response = url.post(line_id=line['id'])
    response.assert_ok()
```

Fixtures will automatically generate the minimal number of parameters required for creating a
resource. Parameters used for creating the resource can be overridden by passing extra arguments to
the fixture

```python
from test_api import fixtures

@fixtures.user(firstname="John")
def test_user_has_a_firstname(user):
    assert user['firstname'] == "John"
```

Test associators
----------------

Associators are helpers that associate 2 resources together. They are used in tests where 2
resources are assumed to have been previously associated. Associators are used as context
managers inside a test. The association will be destroyed when the context manager exits. 

```python
from test_api import fixtures, confd, association

@fixtures.line()
@fixtures.extension()
def test_get_extension_associated_to_line(line, extension):
    with association.line_extension(line, extension):
        url = confd.lines(line['id']).extensions
        response = url.get()
        assert response.item['extension_id'] == extension['id']
```

You can avoid destroying the association by passing the parameter ```check=False```

```python
from test_api import fixtures, confd, association

@fixtures.user()
@fixtures.line()
def test_user_and_line_can_be_dissociated(user, line):
    #we don't need to dissociate since that is what the test does
    with association.user_line(user, line, check=False):
        url = confd.users(user['id']).lines(line['id'])
        response = url.delete()
        response.assert_ok()
```
