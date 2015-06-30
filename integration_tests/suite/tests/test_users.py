from test_api import scenarios as s
from test_api import errors as e
from test_api import confd
from test_api import fixtures
from test_api.helpers.user import generate_user
from test_api.helpers.user_line import user_and_line_associated
from test_api.helpers.line_extension import line_and_extension_associated
from test_api.helpers.line_device import line_and_device_associated

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

        response = confd.users(user['id']).put(firstname='foobar')
        response.assert_ok()
