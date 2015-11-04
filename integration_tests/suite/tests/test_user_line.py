import re

from hamcrest import assert_that, contains, has_entries, has_item

from test_api import scenarios as s
from test_api.helpers.user import generate_user, delete_user
from test_api.helpers.line_sip import generate_line, delete_line
from test_api import confd
from test_api import errors as e
from test_api import fixtures
from test_api import associations as a


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
@fixtures.line_sip
def test_associate_user_line(user, line):
    response = confd.users(user['id']).lines.put(line_id=line['id'])
    response.assert_updated()


@fixtures.user()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
def test_associate_muliple_users_to_line(user1, user2, user3, line):
    response = confd.users(user1['id']).lines.post(line_id=line['id'])
    response.assert_created('users', 'lines')

    response = confd.users(user2['id']).lines.post(line_id=line['id'])
    response.assert_created('users', 'lines')

    response = confd.users(user3['id']).lines.post(line_id=line['id'])
    response.assert_created('users', 'lines')


@fixtures.user()
@fixtures.line_sip()
def test_get_line_associated_to_user(user, line):
    expected = contains(has_entries({'user_id': user['id'],
                                     'line_id': line['id'],
                                     'main_user': True,
                                     'main_line': True}))

    with a.user_line(user, line):
        response = confd.users(user['id']).lines.get()
        assert_that(response.items, expected)


@fixtures.user()
@fixtures.line_sip()
def test_get_user_associated_to_line(user, line):
    expected = contains(has_entries({'user_id': user['id'],
                                     'line_id': line['id'],
                                     'main_user': True,
                                     'main_line': True}))

    with a.user_line(user, line):
        response = confd.lines(line['id']).users.get()
        assert_that(response.items, expected)


@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
def test_get_secondary_user_associated_to_line(main_user, other_user, line):
    expected = has_item(has_entries({'user_id': other_user['id'],
                                     'line_id': line['id'],
                                     'main_user': False,
                                     'main_line': True}))

    with a.user_line(main_user, line), a.user_line(other_user, line):
        response = confd.lines(line['id']).users.get()
        assert_that(response.items, expected)


@fixtures.user()
@fixtures.line_sip()
def test_associate_when_user_already_associated_to_same_line(user, line):
    with a.user_line(user, line):
        response = confd.users(user['id']).lines.post(line_id=line['id'])
        response.assert_match(400, e.resource_associated('User', 'Line'))


@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_when_user_already_associated_to_another_line(user, first_line, second_line):
    with a.user_line(user, first_line):
        response = confd.users(user['id']).lines.post(line_id=first_line['id'])
        response.assert_match(400, e.resource_associated('User', 'Line'))


@fixtures.user()
@fixtures.line()
def test_associate_user_to_line_without_endpoint(user, line):
    response = confd.users(user['id']).lines.post(line_id=line['id'])
    response.assert_match(400, e.missing_association('Line', 'Endpoint'))


@fixtures.user()
@fixtures.line()
@fixtures.sip()
def test_associate_user_to_line_with_endpoint(user, line, sip):
    with a.line_endpoint_sip(line, sip, check=False):
        response = confd.users(user['id']).lines.post(line_id=line['id'])
        response.assert_created('users', 'lines')
        assert_that(response.item, has_entries({'user_id': user['id'],
                                                'line_id': line['id']}))


@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
def test_dissociate_second_user_then_first(first_user, second_user, line):
    with a.user_line(first_user, line, check=False), \
            a.user_line(second_user, line, check=False):
        response = confd.users(second_user['id']).lines(line['id']).delete()
        response.assert_deleted()

        response = confd.users(first_user['id']).lines(line['id']).delete()
        response.assert_deleted()


@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
def test_dissociate_second_user_before_first(first_user, second_user, line):
    with a.user_line(first_user, line), a.user_line(second_user, line):
        response = confd.users(first_user['id']).lines(line['id']).delete()
        response.assert_match(400, secondary_user_regex)


@fixtures.user()
@fixtures.line_sip()
@fixtures.device()
def test_dissociate_user_line_when_device_is_associated(user, line, device):
    with a.user_line(user, line), a.line_device(line, device):
        response = confd.users(user['id']).lines(line['id']).delete()
        response.assert_match(400, e.resource_associated('Line', 'Device'))


@fixtures.user()
@fixtures.line_sip()
def test_delete_user_when_user_and_line_associated(user, line):
    with a.user_line(user, line):
        response = confd.users(user['id']).delete()
        response.assert_match(400, e.resource_associated('User', 'Line'))
