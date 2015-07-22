from test_api import scenarios as s
from test_api import errors as e
from test_api import confd
from test_api import fixtures
from test_api.helpers.user import generate_user
from test_api.helpers.user_line import user_and_line_associated
from test_api.helpers.line_extension import line_and_extension_associated
from test_api.helpers.line_device import line_and_device_associated

from hamcrest import assert_that, equal_to, has_entries, has_entry

FIELDS = ['firstname',
          'lastname',
          'timezone',
          'language',
          'description',
          'caller_id',
          'outgoing_caller_id',
          'mobile_phone_number',
          'username',
          'password',
          'music_on_hold',
          'preprocess_subroutine',
          'userfield']

REQUIRED = ['firstname']

BOGUS = [(f, 123, 'unicode string') for f in FIELDS]

NULL_USER = {"firstname": "John",
             "lastname": None,
             "username": None,
             "mobile_phone_number": None,
             "userfield": None,
             "outgoing_caller_id": None,
             "music_on_hold": None,
             "language": None,
             "timezone": None,
             "preprocess_subroutine": None,
             "password": None,
             "description": None}


class TestUserResource(s.GetScenarios, s.CreateScenarios, s.EditScenarios, s.DeleteScenarios):

    url = "/users"
    resource = "User"
    required = REQUIRED
    bogus_fields = BOGUS

    def create_resource(self):
        user = generate_user()
        return user['id']

    def test_invalid_mobile_phone_number(self):
        response = confd.users.post(firstname='firstname',
                                    mobile_phone_number='ai67cba74cba6kw4acwbc6w7')
        error = e.wrong_type(field='mobile_phone_number',
                             type='numeric phone number')
        response.assert_match(400, error)


@fixtures.user()
@fixtures.line()
@fixtures.extension()
@fixtures.device()
def test_updating_user_when_associated_to_user_and_line(user, line, extension, device):
    with user_and_line_associated(user, line), \
            line_and_extension_associated(line, extension), \
            line_and_device_associated(line, device):

        print user['caller_id']
        response = confd.users(user['id']).put(firstname='foobar')
        response.assert_ok()


def test_create_user_with_all_parameters_null():
    response = confd.users.post(**NULL_USER)
    assert_that(response.item, has_entries(NULL_USER))


@fixtures.user()
def test_update_user_with_all_parameters_null(user):
    response = confd.users(user['id']).put(**NULL_USER)
    response.assert_ok()

    response = confd.users(user['id']).get()
    assert_that(response.item, has_entries(**NULL_USER))


def test_create_user_generates_appropriate_caller_id():
    expected_caller_id = '"John"'
    response = confd.users.post(firstname='John')
    assert_that(response.item, has_entry('caller_id', expected_caller_id))

    expected_caller_id = '"John Doe"'
    response = confd.users.post(firstname='John', lastname='Doe')
    assert_that(response.item['caller_id'], equal_to(expected_caller_id))
