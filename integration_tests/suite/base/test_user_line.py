# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import re

from hamcrest import assert_that
from hamcrest import contains
from hamcrest import contains_inanyorder
from hamcrest import empty
from hamcrest import has_entries
from hamcrest import has_item
from hamcrest import has_entry

from ..test_api import scenarios as s
from . import confd
from ..test_api import errors as e
from ..test_api import helpers as h
from ..test_api import fixtures
from ..test_api import associations as a


secondary_user_regex = re.compile(r"There are secondary users associated to the line")

FAKE_ID = 999999999


@fixtures.user()
@fixtures.line_sip()
def test_associate_errors(user, line):
    fake_user = confd.users(FAKE_ID).lines(line_id=line['id']).post
    fake_line = confd.users(user['id']).lines(line_id=FAKE_ID).post

    yield s.check_resource_not_found, fake_user, 'User'
    yield s.check_bogus_field_returns_error, fake_line, 'line_id', FAKE_ID

    fake_user = confd.users(FAKE_ID).lines(line['id']).put
    fake_line = confd.users(user['id']).lines(FAKE_ID).put

    yield s.check_resource_not_found, fake_user, 'User'
    yield s.check_resource_not_found, fake_line, 'Line'


@fixtures.user()
@fixtures.line_sip()
def test_dissociate_errors(user, line):
    fake_user = confd.users(FAKE_ID).lines(line['id']).delete
    fake_line = confd.users(user['id']).lines(FAKE_ID).delete

    yield s.check_resource_not_found, fake_user, 'User'
    yield s.check_resource_not_found, fake_line, 'Line'


def test_get_errors():
    fake_user = confd.users(FAKE_ID).lines.get
    fake_line = confd.lines(FAKE_ID).users.get

    yield s.check_resource_not_found, fake_user, 'User'
    yield s.check_resource_not_found, fake_line, 'Line'


@fixtures.user()
@fixtures.line_sip()
def test_associate_user_line(user, line):
    response = confd.users(user['id']).lines(line['id']).put()
    response.assert_updated()


@fixtures.user()
@fixtures.line_sip()
def test_associate_user_line_using_deprecated(user, line):
    response = confd.users(user['id']).lines.post(line_id=line['id'])
    response.assert_created('users', 'lines')


@fixtures.user()
@fixtures.line_sip()
def test_associate_using_uuid(user, line):
    response = confd.users(user['uuid']).lines(line['id']).put()
    response.assert_updated()


@fixtures.user()
@fixtures.line_sip()
def test_associate_user_line_using_uuid_and_deprecated(user, line):
    response = confd.users(user['uuid']).lines.post(line_id=line['id'])
    response.assert_created('users', 'lines')


@fixtures.user()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_associate_muliple_users_to_line(user1, user2, user3, line, extension):
    with a.line_extension(line, extension):
        response = confd.users(user1['id']).lines(line['id']).put()
        response.assert_updated()

        response = confd.users(user2['id']).lines(line['id']).put()
        response.assert_updated()

        response = confd.users(user3['id']).lines(line['id']).put()
        response.assert_updated()


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

        response = confd.users(user['uuid']).lines.get()
        assert_that(response.items, expected)


@fixtures.user()
@fixtures.line_sip()
def test_get_line_after_dissociation(user, line):
    h.user_line.associate(user['id'], line['id'])
    h.user_line.dissociate(user['id'], line['id'])

    response = confd.users(user['id']).lines.get()
    assert_that(response.items, empty())

    response = confd.users(user['uuid']).lines.get()
    assert_that(response.items, empty())


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
        response = confd.users(user['id']).lines(line['id']).put()
        response.assert_match(400, e.resource_associated('User', 'Line'))


@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_user_to_multiple_lines(user, line1, line2, line3):
    response = confd.users(user['id']).lines(line1['id']).put()
    response.assert_updated()

    response = confd.users(user['id']).lines(line2['id']).put()
    response.assert_updated()

    response = confd.users(user['id']).lines(line3['id']).put()
    response.assert_updated()

    response = confd.users(user['id']).lines.get()
    assert_that(response.items, contains_inanyorder(has_entries({'line_id': line1['id'],
                                                                 'main_line': True}),
                                                    has_entries({'line_id': line2['id'],
                                                                 'main_line': False}),
                                                    has_entries({'line_id': line3['id'],
                                                                 'main_line': False})))


@fixtures.user()
@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_user_to_multiple_lines_with_same_extension(user, extension, line1, line2):
    with a.line_extension(line1, extension), a.line_extension(line2, extension):
        response = confd.users(user['id']).lines(line1['id']).put()
        response.assert_updated()

        response = confd.users(user['id']).lines(line2['id']).put()
        response.assert_updated()


@fixtures.user()
@fixtures.extension()
@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_user_to_multiple_lines_with_different_extension(user, extension1, extension2, line1, line2):
    with a.line_extension(line1, extension1), a.line_extension(line2, extension2):
        response = confd.users(user['id']).lines(line1['id']).put()
        response.assert_updated()

        response = confd.users(user['id']).lines(line2['id']).put()
        response.assert_updated()


@fixtures.user()
@fixtures.user()
@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_two_users_to_two_lines_with_same_extension(user1, user2, extension, line1, line2):
    with a.line_extension(line1, extension), a.line_extension(line2, extension):
        response = confd.users(user1['id']).lines(line1['id']).put()
        response.assert_updated()

        response = confd.users(user2['id']).lines(line2['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Extension'))


@fixtures.user()
@fixtures.line()
def test_associate_user_to_line_without_endpoint(user, line):
    response = confd.users(user['id']).lines(line['id']).put()
    response.assert_match(400, e.missing_association('Line', 'Endpoint'))


@fixtures.user()
@fixtures.line()
@fixtures.sip()
def test_associate_user_to_line_with_endpoint(user, line, sip):
    with a.line_endpoint_sip(line, sip, check=False):
        response = confd.users(user['id']).lines(line['id']).put()
        response.assert_updated()
        response = confd.users(user['id']).lines.get()
        assert_that(response.items, contains(has_entries({'user_id': user['id'],
                                                          'line_id': line['id']})))


@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_lines_to_user(user, line1, line2):
    response = confd.users(user['uuid']).lines.put(lines=[line2, line1])
    response.assert_updated()
    response = confd.users(user['uuid']).get()
    assert_that(response.item['lines'], contains(has_entries({'id': line2['id']}),
                                                 has_entries({'id': line1['id']})))


@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_lines_to_swap_main_line(user, line1, line2):
    response = confd.users(user['uuid']).lines.put(lines=[line1, line2])
    response.assert_updated()
    response = confd.users(user['uuid']).get()
    assert_that(response.item['lines'], contains(has_entries({'id': line1['id']}),
                                                 has_entries({'id': line2['id']})))
    response = confd.users(user['uuid']).lines.put(lines=[line2, line1])
    response.assert_updated()
    response = confd.users(user['uuid']).get()
    assert_that(response.item['lines'], contains(has_entries({'id': line2['id']}),
                                                 has_entries({'id': line1['id']})))


@fixtures.user()
@fixtures.line_sip()
def test_associate_lines_twice_with_same_line(user, line):
    response = confd.users(user['uuid']).lines.put(lines=[line])
    response.assert_updated()
    response = confd.users(user['uuid']).lines.put(lines=[line])
    response.assert_updated()


@fixtures.user()
@fixtures.line_sip()
def test_associate_lines_same_line(user, line):
    response = confd.users(user['uuid']).lines.put(lines=[line, line])
    response.assert_status(400)


# Tests that /users/id/lines execute the same validator as /users/id/lines/id
@fixtures.user()
@fixtures.line()
def test_associate_lines_without_endpoint(user, line):
    response = confd.users(user['uuid']).lines.put(lines=[line])
    response.assert_match(400, e.missing_association('Line', 'Endpoint'))


# Tests that /users/id/lines execute the same validator as /users/id/lines/id
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
def test_dissociate_lines_second_user_before_first(user1, user2, line):
    with a.user_line(user1, line), a.user_line(user2, line):
        response = confd.users(user1['uuid']).lines.put(lines=[])
        response.assert_match(400, secondary_user_regex)


@fixtures.user()
@fixtures.line_sip()
def test_dissociate_using_uuid(user, line):
    with a.user_line(user, line, check=False):
        response = confd.users(user['uuid']).lines(line['id']).delete()
        response.assert_deleted()


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
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.line_sip()
def test_dissociate_main_line_then_main_line_fallback_to_secondary(user, line1, line2, line3):
    with a.user_line(user, line1, check=False), \
            a.user_line(user, line2, check=False), \
            a.user_line(user, line3, check=False):
        response = confd.users(user['id']).lines.get()
        assert_that(response.items, contains_inanyorder(has_entries({'line_id': line1['id'],
                                                                     'main_line': True}),
                                                        has_entries({'line_id': line2['id'],
                                                                     'main_line': False}),
                                                        has_entries({'line_id': line3['id'],
                                                                     'main_line': False})))

        confd.users(user['uuid']).lines(line1['id']).delete().assert_deleted()
        response = confd.users(user['uuid']).lines.get()
        assert_that(response.items, has_item(has_entry('main_line', True)))

        confd.users(user['uuid']).lines(line2['id']).delete().assert_deleted()
        response = confd.users(user['uuid']).lines.get()
        assert_that(response.items, has_item(has_entry('main_line', True)))

        confd.users(user['uuid']).lines(line3['id']).delete().assert_deleted()
        response = confd.users(user['uuid']).lines.get()
        assert_that(response.items, empty())


@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
def test_dissociate_second_user_before_first(first_user, second_user, line):
    with a.user_line(first_user, line), a.user_line(second_user, line):
        response = confd.users(first_user['id']).lines(line['id']).delete()
        response.assert_match(400, secondary_user_regex)


@fixtures.user()
@fixtures.line_sip()
def test_get_users_relation(user, line):
    expected = has_entries(
        users=contains(has_entries(uuid=user['uuid'],
                                   firstname=user['firstname'],
                                   lastname=user['lastname']))
    )

    with a.user_line(user, line):
        response = confd.lines(line['id']).get()
        assert_that(response.item, expected)


@fixtures.user()
@fixtures.line_sip()
def test_get_lines_relation(user, line):
    line = confd.lines(line['id']).get().item
    expected = has_entries(
        lines=contains(has_entries(id=line['id'],
                                   endpoint_sip=line['endpoint_sip'],
                                   endpoint_sccp=line['endpoint_sccp'],
                                   endpoint_custom=line['endpoint_custom'],
                                   extensions=line['extensions']))
    )

    with a.user_line(user, line):
        response = confd.users(user['id']).get()
        assert_that(response.item, expected)


@fixtures.user()
@fixtures.line_sip()
def test_delete_user_when_user_and_line_associated(user, line):
    with a.user_line(user, line):
        response = confd.users(user['id']).delete()
        response.assert_match(400, e.resource_associated('User', 'Line'))
