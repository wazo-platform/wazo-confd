# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import assert_that, contains_inanyorder, equal_to, has_entries

from ..helpers import associations as a
from ..helpers import fixtures
from . import confd


@fixtures.user()
@fixtures.line()
@fixtures.sip()
def test_get_user_line_id_associated_endpoints_sip(user, line, sip):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line):
        response = (
            confd.users(user['uuid']).lines(line['id']).associated.endpoints.sip.get()
        )
        assert_that(
            response.item,
            has_entries(uuid=sip['uuid']),
        )


@fixtures.user()
@fixtures.line()
@fixtures.sip()
def test_get_merged_view_validation(user, line, sip):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line):
        response = (
            confd.users(user['uuid'])
            .lines(line['id'])
            .associated.endpoints.sip.get(view='unknown')
        )
        response.assert_match(400, re.compile(re.escape('Must be one of: merged.')))


@fixtures.user()
@fixtures.line()
@fixtures.sip_template(aor_section_options=[['max_contacts', '42']])
@fixtures.sip(label='Inherited')
def test_get_merged_view(user, line, template, sip):
    with a.line_endpoint_sip(line, sip), a.user_line(
        user, line
    ), a.endpoint_sip_template_sip(sip, template):
        response = (
            confd.users(user['uuid'])
            .lines(line['id'])
            .associated.endpoints.sip.get(view='merged')
        )
        assert_that(
            response.item,
            has_entries(
                uuid=sip['uuid'],
                aor_section_options=contains_inanyorder(['max_contacts', '42']),
            ),
        )


@fixtures.user()
@fixtures.line()
@fixtures.sccp()
def test_get_user_line_id_associated_endpoints_sip_when_endpoint_is_sccp(
    user, line, sccp
):
    with a.line_endpoint_sccp(line, sccp), a.user_line(user, line):
        response = (
            confd.users(user['uuid'])
            .lines(line['id'])
            .main.associated.endpoints.sip.get()
        )
        assert_that(response.status, equal_to(404))


@fixtures.user()
def test_get_user_line_id_associated_endpoints_sip_when_line_does_not_exist(user):
    response = confd.users(user['uuid']).lines(999999).associated.endpoints.sip.get()
    assert_that(response.status, equal_to(404))


@fixtures.user()
@fixtures.line()
@fixtures.sip()
def test_get_user_line_id_associated_endpoints_sip_when_user_line_not_associated(
    user, line, sip
):
    with a.line_endpoint_sip(line, sip):
        response = (
            confd.users(user['uuid']).lines(line['id']).associated.endpoints.sip.get()
        )
        assert_that(response.status, equal_to(404))


@fixtures.user()
@fixtures.line()
@fixtures.sip()
def test_get_user_line_main_associated_endpoints_sip(user, line, sip):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line):
        response = confd.users(user['uuid']).lines.main.associated.endpoints.sip.get()
        assert_that(response.item, has_entries(uuid=sip['uuid']))


@fixtures.user()
@fixtures.line()
@fixtures.sccp()
def test_get_user_line_main_associated_endpoints_sip_when_endpoint_is_sccp(
    user, line, sccp
):
    with a.line_endpoint_sccp(line, sccp), a.user_line(user, line):
        response = confd.users(user['uuid']).lines.main.associated.endpoints.sip.get()
        assert_that(response.status, equal_to(404))


@fixtures.user()
def test_get_user_line_main_associated_endpoints_sip_when_line_does_not_exist(user):
    response = confd.users(user['uuid']).lines.main.associated.endpoints.sip.get()
    assert_that(response.status, equal_to(404))
