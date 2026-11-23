# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_exactly,
    contains_inanyorder,
    empty,
    has_entries,
)

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT, SUB_TENANT2
from . import confd

FAKE_ID = 999999999
FAKE_UUID = '99999999-9999-9999-9999-999999999999'


@fixtures.group()
@fixtures.user()
def test_associate_errors(group, user):
    response = confd.users(FAKE_UUID).groups.put(groups=[group])
    response.assert_status(404)

    url = confd.users(user['uuid']).groups
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'groups', 123)
    s.check_bogus_field_returns_error(url, 'groups', None)
    s.check_bogus_field_returns_error(url, 'groups', True)
    s.check_bogus_field_returns_error(url, 'groups', 'string')
    s.check_bogus_field_returns_error(url, 'groups', [123])
    s.check_bogus_field_returns_error(url, 'groups', [None])
    s.check_bogus_field_returns_error(url, 'groups', ['string'])
    s.check_bogus_field_returns_error(url, 'groups', [{}])
    s.check_bogus_field_returns_error(url, 'groups', [{'id': None}])
    s.check_bogus_field_returns_error(url, 'groups', [{'id': 1}, {'uuid': None}])
    s.check_bogus_field_returns_error(url, 'groups', [{'not_id': 123}])
    s.check_bogus_field_returns_error(url, 'groups', [{'id': FAKE_UUID}])


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_associate(group, user, line):
    with a.user_line(user, line):
        response = confd.users(user['uuid']).groups.put(groups=[group])
        response.assert_updated()


@fixtures.group()
@fixtures.group()
@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_associate_multiple(group1, group2, group3, user, line):
    with a.user_line(user, line):
        response = confd.users(user['uuid']).groups.put(groups=[group1, group2, group3])
        response.assert_updated()

        response = confd.users(user['uuid']).get()
        assert_that(
            response.item,
            has_entries(
                groups=contains_inanyorder(
                    has_entries(id=group1['id']),
                    has_entries(id=group2['id']),
                    has_entries(id=group3['id']),
                )
            ),
        )


@fixtures.group()
@fixtures.user()
def test_associate_user_with_no_line(group, user):
    response = confd.users(user['uuid']).groups.put(groups=[group])
    response.assert_match(400, e.missing_association('User', 'Line'))


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_associate_same_group(group, user, line):
    with a.user_line(user, line):
        response = confd.users(user['uuid']).groups.put(group=[group, group])
        response.assert_status(400)


@fixtures.group()
@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_dissociate(group1, group2, user, line):
    with a.user_line(user, line), a.group_member_user(
        group1, user
    ), a.group_member_user(group2, user):
        response = confd.users(user['uuid']).groups.put(groups=[])
        response.assert_updated()


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_dissociate_with_multi_line_user(group, user, line_1, line_2):
    with a.user_line(user, line_1), a.user_line(user, line_2, check=False):
        with a.group_member_user(group, user):
            # The group member is the interface of the main line of the user.
            # Deleting the any secondary line should keep the user in the group
            # Deleting the main line will remove the user from the group
            response = confd.lines(line_2['id']).delete()
            response.assert_deleted()

            response = confd.users(user['uuid']).get()
            assert_that(
                response.item,
                has_entries(
                    groups=contains_inanyorder(
                        has_entries(id=group['id']),
                    )
                ),
            )


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_bus_events(group, user, line):
    with a.user_line(user, line):
        url = confd.users(user['uuid']).groups.put
        body = {'groups': [group]}
        headers = {
            'tenant_uuid': user['tenant_uuid'],
            f'user_uuid:{user["uuid"]}': True,
        }

        s.check_event('user_groups_associated', headers, url, body)


def put_groups(user, groups):
    def call(query=None, **kwargs):
        url = confd.users(user['uuid']).groups
        return url.put(groups=groups, query_string=query, **kwargs)

    return call


def group_ids_of(user):
    return [group['id'] for group in confd.users(user['uuid']).get().item['groups']]


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT2)
def test_associate_user_outside_tenant(main_user, sibling_user):
    for user in (main_user, sibling_user):
        s.check_outside_tenant_not_found(put_groups(user, []), 'User', SUB_TENANT)


@fixtures.context(wazo_tenant=SUB_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_associate_sub_tenant_user_from_main_tenant(sub_context, sub_group, sub_user):
    @fixtures.line_sip(context=sub_context, wazo_tenant=SUB_TENANT)
    def aux(sub_line):
        with a.user_line(sub_user, sub_line):
            call = put_groups(sub_user, [sub_group])
            s.check_sub_tenant_found_only_with_recurse(call, 'User', MAIN_TENANT, 204)
            assert_that(group_ids_of(sub_user), contains_exactly(sub_group['id']))

            put_groups(sub_user, [])(wazo_tenant=SUB_TENANT).assert_updated()

    aux()


@fixtures.context(wazo_tenant=SUB_TENANT)
@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT2)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_associate_group_outside_tenant(
    sub_context, main_group, sub_group, sibling_group, sub_user
):
    @fixtures.line_sip(context=sub_context, wazo_tenant=SUB_TENANT)
    def aux(sub_line):
        with a.user_line(sub_user, sub_line):
            put_groups(sub_user, [sub_group])(wazo_tenant=SUB_TENANT).assert_updated()

            for outside in (main_group, sibling_group):
                for query in (None, {'recurse': 'true'}):
                    call = put_groups(sub_user, [outside])
                    response = call(query, wazo_tenant=SUB_TENANT)
                    response.assert_match(400, e.not_found('Group'))
                    assert_that(
                        group_ids_of(sub_user), contains_exactly(sub_group['id'])
                    )

            put_groups(sub_user, [])(wazo_tenant=SUB_TENANT).assert_updated()

    aux()


@fixtures.context(wazo_tenant=MAIN_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT)
@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_associate_groups_of_different_tenants(
    main_context, sub_context, main_group, sub_group, main_user, sub_user
):
    @fixtures.line_sip(context=main_context, wazo_tenant=MAIN_TENANT)
    @fixtures.line_sip(context=sub_context, wazo_tenant=SUB_TENANT)
    def aux(main_line, sub_line):
        with a.user_line(main_user, main_line), a.user_line(sub_user, sub_line):
            response = put_groups(main_user, [sub_group])(wazo_tenant=MAIN_TENANT)
            response.assert_match(400, e.not_found('Group'))

            recurse = {'recurse': 'true'}
            call = put_groups(main_user, [sub_group])
            response = call(recurse, wazo_tenant=MAIN_TENANT)
            response.assert_match(400, e.different_tenant())
            call = put_groups(sub_user, [main_group])
            response = call(recurse, wazo_tenant=MAIN_TENANT)
            response.assert_match(400, e.different_tenant())

            assert_that(group_ids_of(main_user), empty())
            assert_that(group_ids_of(sub_user), empty())

    aux()


@fixtures.user(wazo_tenant=SUB_TENANT)
def test_associate_recurse_is_boolean(sub_user):
    s.check_recurse_is_boolean(put_groups(sub_user, []), SUB_TENANT)


@fixtures.user(wazo_tenant=SUB_TENANT2)
def test_associate_wazo_tenant_not_visible(sibling_user):
    s.check_wazo_tenant_not_visible_refused(put_groups(sibling_user, []))
