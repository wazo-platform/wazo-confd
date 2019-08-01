# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_items, has_entries

from . import confd
from ..helpers import (
    associations as a,
    fixtures,
)


def test_associate_user_then_line_then_extension():
    with fixtures.user() as user, fixtures.line_sip() as line, fixtures.extension() as extension:
        response = confd.users(user['id']).lines.post(line_id=line['id'])
        response.assert_created('users', 'lines')

        response = confd.lines(line['id']).extensions.post(extension_id=extension['id'])
        response.assert_created('lines', 'extensions')



def test_associate_extension_then_line_then_user():
    with fixtures.user() as user, fixtures.line_sip() as line, fixtures.extension() as extension:
        response = confd.lines(line['id']).extensions.post(extension_id=extension['id'])
        response.assert_created('lines', 'extensions')

        response = confd.users(user['id']).lines.post(line_id=line['id'])
        response.assert_created('users', 'lines')



def test_dissociate_user_then_line_then_extension():
    with fixtures.user() as user, fixtures.line_sip() as line, fixtures.extension() as extension:
        with a.user_line(user, line, check=False), a.line_extension(line, extension, check=False):

            response = confd.users(user['id']).lines(line['id']).delete()
            response.assert_deleted()

            response = confd.lines(line['id']).extensions(extension['id']).delete()
            response.assert_deleted()


def test_dissociate_extension_then_line_then_user():
    with fixtures.user() as user, fixtures.line_sip() as line, fixtures.extension() as extension:
        with a.user_line(user, line, check=False), a.line_extension(line, extension, check=False):

            response = confd.lines(line['id']).extensions(extension['id']).delete()
            response.assert_deleted()

            response = confd.users(user['id']).lines(line['id']).delete()
            response.assert_deleted()


def test_get_line_extension_associations():
    with fixtures.user() as user, fixtures.line_sip() as line, fixtures.extension(context='default') as extension:
        with a.user_line(user, line), a.line_extension(line, extension):
            response = confd.lines(line['id']).extensions.get()
            assert_that(
                response.items,
                has_items(has_entries(
                    line_id=line['id'],
                    extension_id=extension['id'],
                ))
            )


def test_caller_name_on_sip_line():
    with fixtures.user(firstname="Jôhn", lastname="Smîth") as user, fixtures.line() as line, fixtures.sip() as sip, fixtures.extension() as extension:
        with a.line_endpoint_sip(line, sip), a.user_line(user, line), a.line_extension(line, extension):
            response = confd.lines(line['id']).get()
            assert_that(response.item, has_entries({'caller_id_name': 'Jôhn Smîth',
                                                    'caller_id_num': extension['exten']}))


def test_caller_id_on_sip_line():
    with fixtures.user(caller_id='"Jôhn Smîth" <1000>') as user, fixtures.line() as line, fixtures.sip() as sip, fixtures.extension() as extension:
        with a.line_endpoint_sip(line, sip), a.user_line(user, line), a.line_extension(line, extension):
            response = confd.lines(line['id']).get()
            assert_that(response.item, has_entries({'caller_id_name': 'Jôhn Smîth',
                                                    'caller_id_num': '1000'}))


def test_caller_name_on_sccp_line():
    with fixtures.user(firstname="Jôhn", lastname="Smîth") as user, fixtures.line() as line, fixtures.sccp() as sccp, fixtures.extension() as extension:
        with a.line_endpoint_sccp(line, sccp), a.user_line(user, line), a.line_extension(line, extension):
            response = confd.lines(line['id']).get()
            assert_that(response.item, has_entries({'caller_id_name': 'Jôhn Smîth',
                                                    'caller_id_num': extension['exten']}))


def test_caller_id_on_sccp_line():
    with fixtures.user(caller_id='"Jôhn Smîth" <1000>') as user, fixtures.line() as line, fixtures.sccp() as sccp, fixtures.extension() as extension:
        with a.line_endpoint_sccp(line, sccp), a.user_line(user, line), a.line_extension(line, extension):
            response = confd.lines(line['id']).get()
            assert_that(response.item, has_entries({'caller_id_name': 'Jôhn Smîth',
                                                    'caller_id_num': extension['exten']}))


def test_associating_two_sccp_lines_with_users_does_not_make_the_db_fail():
    with fixtures.user() as user1, fixtures.user() as user2, fixtures.line() as line1, fixtures.line() as line2, fixtures.sccp() as sccp1, fixtures.sccp() as sccp2:
        with a.line_endpoint_sccp(line1, sccp1, check=False), a.line_endpoint_sccp(line2, sccp2, check=False):
            response = confd.users(user1['id']).lines.post(line_id=line1['id'])
            response.assert_ok()

            response = confd.users(user2['id']).lines.post(line_id=line2['id'])
            response.assert_ok()
