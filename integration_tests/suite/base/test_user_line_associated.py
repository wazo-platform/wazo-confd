# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import assert_that, contains_inanyorder, equal_to, has_entries

from ..helpers import associations as a
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT, SUB_TENANT2
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


def get_endpoint_sip(user, line_id):
    def call(query=None, **kwargs):
        url = confd.users(user['uuid']).lines(line_id).associated.endpoints.sip
        return url.get(**(query or {}), **kwargs)

    return call


@fixtures.context(wazo_tenant=MAIN_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT2)
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT2)
def test_get_associated_endpoints_sip_outside_tenant(
    main_context, sibling_context, main_user, sibling_user
):
    @fixtures.line_sip(context=main_context, wazo_tenant=MAIN_TENANT)
    @fixtures.line_sip(context=sibling_context, wazo_tenant=SUB_TENANT2)
    def aux(main_line, sibling_line):
        with a.user_line(main_user, main_line):
            with a.user_line(sibling_user, sibling_line):
                for user, line in (
                    (main_user, main_line),
                    (sibling_user, sibling_line),
                ):
                    for line_id in (line['id'], 'main'):
                        call = get_endpoint_sip(user, line_id)
                        s.check_outside_tenant_not_found(
                            call, 'UserFeatures', SUB_TENANT
                        )

    aux()


@fixtures.context(wazo_tenant=SUB_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_get_associated_endpoints_sip_sub_tenant_from_main_tenant(
    sub_context, sub_user
):
    @fixtures.line_sip(context=sub_context, wazo_tenant=SUB_TENANT)
    def aux(sub_line):
        with a.user_line(sub_user, sub_line):
            for line_id in (sub_line['id'], 'main'):
                call = get_endpoint_sip(sub_user, line_id)
                s.check_sub_tenant_found_only_with_recurse(
                    call, 'UserFeatures', MAIN_TENANT, 200
                )

    aux()


@fixtures.user(wazo_tenant=SUB_TENANT)
def test_get_associated_endpoints_sip_recurse_is_boolean(sub_user):
    s.check_recurse_is_boolean(get_endpoint_sip(sub_user, 'main'), SUB_TENANT)


@fixtures.user(wazo_tenant=SUB_TENANT2)
def test_get_associated_endpoints_sip_wazo_tenant_not_visible(sibling_user):
    call = get_endpoint_sip(sibling_user, 'main')
    s.check_wazo_tenant_not_visible_refused(call)
