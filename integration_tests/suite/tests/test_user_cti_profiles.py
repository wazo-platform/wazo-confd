from test_api import confd
from test_api import fixtures
from test_api import errors as e
import re

FAKE_ID = 999999999

missing_username_password_regex = re.compile(r"User must have a username and password to enable a CtiProfile")


def test_get_when_user_does_not_exist():
    response = confd.users(FAKE_ID).cti.get()
    response.assert_match(404, e.not_found('User'))


@fixtures.user()
def test_associate_user_with_fake_cti_profile(user):
    url = confd.users(user['id']).cti
    response = url.put(cti_profile_id=FAKE_ID)
    response.assert_match(400, e.not_found('CtiProfile'))


@fixtures.user(username=None, password=None)
def test_enable_cti_for_user_without_username_or_password(user):
    url = confd.users(user['id']).cti
    response = url.put(enabled=True)
    response.assert_match(400, missing_username_password_regex)
