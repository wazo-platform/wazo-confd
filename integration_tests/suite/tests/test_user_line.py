import re

from hamcrest import assert_that, contains, has_entries

from test_api import scenarios as s
from test_api.helpers.user import generate_user, delete_user
from test_api.helpers.line import generate_line, delete_line
from test_api.helpers.user_line import user_and_line_associated
from test_api.helpers.line_device import line_and_device_associated
from test_api import confd
from test_api import errors as e
from test_api import fixtures


secondary_user_regex = re.compile(r"There are secondary users associated to the line")

FAKE_ID = 999999999


class TestUserLineAssociation(s.AssociationScenarios, s.DissociationCollectionScenarios, s.AssociationGetCollectionScenarios):

    left_resource = "User"
    right_resource = "Line"

    def create_resources(self):
        user = generate_user()
        line = generate_line()
        return user['id'], line['id']

    def delete_resources(self, user_id, line_id):
        delete_user(user_id)
        delete_line(line_id)

    def associate_resources(self, user_id, line_id):
        return confd.users(user_id).lines.post(line_id=line_id)

    def dissociate_resources(self, user_id, line_id):
        return confd.users(user_id).lines(line_id).delete()

    def get_association(self, user_id, line_id):
        return confd.users(user_id).lines.get()


@fixtures.user
@fixtures.line
def test_associate_user_line(user, line):
    response = confd.users(user['id']).lines.put(line_id=line['id'])
    response.assert_ok()


@fixtures.user()
@fixtures.user()
@fixtures.user()
@fixtures.line()
def test_associate_muliple_users_to_line(user1, user2, user3, line):
    response = confd.users(user1['id']).lines.post(line_id=line['id'])
    response.assert_ok()

    response = confd.users(user2['id']).lines.post(line_id=line['id'])
    response.assert_ok()

    response = confd.users(user3['id']).lines.post(line_id=line['id'])
    response.assert_ok()


@fixtures.user()
@fixtures.line()
def test_get_line_associated_to_user(user, line):
    expected = contains(has_entries({'user_id': user['id'],
                                     'line_id': line['id'],
                                     'main_user': True,
                                     'main_line': True}))

    with user_and_line_associated(user, line):
        response = confd.users(user['id']).lines.get()
        assert_that(response.items, expected)


@fixtures.user()
@fixtures.line()
def test_associate_when_user_already_associated_to_same_line(user, line):
    with user_and_line_associated(user, line):
        response = confd.users(user['id']).lines.post(line_id=line['id'])
        response.assert_match(400, e.resource_associated('User', 'Line'))


@fixtures.user()
@fixtures.line()
@fixtures.line()
def test_associate_when_user_already_associated_to_another_line(user, first_line, second_line):
    with user_and_line_associated(user, first_line):
        response = confd.users(user['id']).lines.post(line_id=first_line['id'])
        response.assert_match(400, e.resource_associated('User', 'Line'))


@fixtures.user()
@fixtures.user()
@fixtures.line()
def test_dissociate_second_user_then_first(first_user, second_user, line):
    with user_and_line_associated(first_user, line, check=False), \
            user_and_line_associated(second_user, line, check=False):
        response = confd.users(second_user['id']).lines(line['id']).delete()
        response.assert_ok()

        response = confd.users(first_user['id']).lines(line['id']).delete()
        response.assert_ok()


@fixtures.user()
@fixtures.user()
@fixtures.line()
def test_dissociate_second_user_before_first(first_user, second_user, line):
    with user_and_line_associated(first_user, line), user_and_line_associated(second_user, line):
        response = confd.users(first_user['id']).lines(line['id']).delete()
        response.assert_match(400, secondary_user_regex)


@fixtures.user()
@fixtures.line()
@fixtures.device()
def test_dissociate_user_line_when_device_is_associated(user, line, device):
    with user_and_line_associated(user, line), line_and_device_associated(line, device):
        response = confd.users(user['id']).lines(line['id']).delete()
        response.assert_match(400, e.resource_associated('Line', 'Device'))


@fixtures.user()
@fixtures.line()
def test_delete_user_when_user_and_line_associated(user, line):
    with user_and_line_associated(user, line):
        response = confd.users(user['id']).delete()
        response.assert_match(400, e.resource_associated('User', 'Line'))
