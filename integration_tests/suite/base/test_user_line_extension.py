# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from ..helpers import associations as a
from ..helpers import fixtures
from . import confd


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_associate_user_then_line_then_extension(user, line, extension):
    response = confd.users(user['id']).lines(line['id']).put()
    response.assert_updated()

    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_associate_extension_then_line_then_user(user, line, extension):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_updated()

    response = confd.users(user['id']).lines(line['id']).put()
    response.assert_updated()


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_dissociate_user_then_line_then_extension(user, line, extension):
    with a.user_line(user, line, check=False), a.line_extension(
        line, extension, check=False
    ):
        response = confd.users(user['id']).lines(line['id']).delete()
        response.assert_deleted()

        response = confd.lines(line['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_dissociate_extension_then_line_then_user(user, line, extension):
    with a.user_line(user, line, check=False), a.line_extension(
        line, extension, check=False
    ):
        response = confd.lines(line['id']).extensions(extension['id']).delete()
        response.assert_deleted()

        response = confd.users(user['id']).lines(line['id']).delete()
        response.assert_deleted()


@fixtures.user(firstname="Jôhn", lastname="Smîth")
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_caller_name_on_sip_line(user, line, sip, extension):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line), a.line_extension(
        line, extension
    ):
        response = confd.lines(line['id']).get()
        assert_that(
            response.item,
            has_entries(
                {'caller_id_name': 'Jôhn Smîth', 'caller_id_num': extension['exten']}
            ),
        )


@fixtures.user(caller_id='"Jôhn Smîth" <1000>')
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_caller_id_on_sip_line(user, line, sip, extension):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line), a.line_extension(
        line, extension
    ):
        response = confd.lines(line['id']).get()
        assert_that(
            response.item,
            has_entries({'caller_id_name': 'Jôhn Smîth', 'caller_id_num': '1000'}),
        )


@fixtures.user(firstname="Jôhn", lastname="Smîth")
@fixtures.line()
@fixtures.sccp()
@fixtures.extension()
def test_caller_name_on_sccp_line(user, line, sccp, extension):
    with a.line_endpoint_sccp(line, sccp), a.user_line(user, line), a.line_extension(
        line, extension
    ):
        response = confd.lines(line['id']).get()
        assert_that(
            response.item,
            has_entries(
                {'caller_id_name': 'Jôhn Smîth', 'caller_id_num': extension['exten']}
            ),
        )


@fixtures.user(caller_id='"Jôhn Smîth" <1000>')
@fixtures.line()
@fixtures.sccp()
@fixtures.extension()
def test_caller_id_on_sccp_line(user, line, sccp, extension):
    with a.line_endpoint_sccp(line, sccp), a.user_line(user, line), a.line_extension(
        line, extension
    ):
        response = confd.lines(line['id']).get()
        assert_that(
            response.item,
            has_entries(
                {'caller_id_name': 'Jôhn Smîth', 'caller_id_num': extension['exten']}
            ),
        )


@fixtures.user()
@fixtures.user()
@fixtures.line()
@fixtures.line()
@fixtures.sccp()
@fixtures.sccp()
def test_associating_two_sccp_lines_with_users_does_not_make_the_db_fail(
    user1, user2, line1, line2, sccp1, sccp2
):
    with a.line_endpoint_sccp(line1, sccp1, check=False), a.line_endpoint_sccp(
        line2, sccp2, check=False
    ):
        response = confd.users(user1['id']).lines(line1['id']).put()
        response.assert_ok()

        response = confd.users(user2['id']).lines(line2['id']).put()
        response.assert_ok()
