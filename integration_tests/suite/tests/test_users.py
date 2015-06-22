from test_api import scenarios as s
from test_api import errors as e
from test_api.helpers.user import generate_user
from test_api import confd

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
