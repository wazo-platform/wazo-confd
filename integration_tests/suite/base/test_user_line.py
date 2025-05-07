# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import assert_that, contains, empty, has_entries

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd

secondary_user_regex = re.compile(r"There are secondary users associated to the line")

FAKE_ID = 999999999


@fixtures.user()
@fixtures.line_sip()
def test_associate_errors(user, line):
    fake_user = confd.users(FAKE_ID).lines(line['id']).put
    fake_line = confd.users(user['id']).lines(FAKE_ID).put

    s.check_resource_not_found(fake_user, 'User')
    s.check_resource_not_found(fake_line, 'Line')


@fixtures.user()
@fixtures.line_sip()
def test_dissociate_errors(user, line):
    fake_user = confd.users(FAKE_ID).lines(line['id']).delete
    fake_line = confd.users(user['id']).lines(FAKE_ID).delete

    s.check_resource_not_found(fake_user, 'User')
    s.check_resource_not_found(fake_line, 'Line')


@fixtures.user()
@fixtures.line_sip()
def test_associate_user_line(user, line):
    response = confd.users(user['id']).lines(line['id']).put()
    response.assert_updated()


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_context, sub_context, main_user, sub_user):
    @fixtures.line_sip(context=main_context, wazo_tenant=MAIN_TENANT)
    @fixtures.line_sip(context=sub_context, wazo_tenant=SUB_TENANT)
    def aux(main_line, sub_line):
        response = (
            confd.users(sub_user['id'])
            .lines(main_line['id'])
            .put(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Line'))

        response = (
            confd.users(main_user['id'])
            .lines(sub_line['id'])
            .put(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('User'))

        response = (
            confd.users(main_user['id'])
            .lines(sub_line['id'])
            .put(wazo_tenant=MAIN_TENANT)
        )
        response.assert_match(400, e.different_tenant())

    aux()


@fixtures.user()
@fixtures.line_sip()
def test_associate_using_uuid(user, line):
    response = confd.users(user['uuid']).lines(line['id']).put()
    response.assert_updated()


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
def test_associate_when_user_already_associated_to_same_line(user, line):
    with a.user_line(user, line):
        response = confd.users(user['id']).lines(line['id']).put()
        response.assert_updated()


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

    response = confd.users(user['id']).get()
    assert_that(
        response.item,
        has_entries(
            lines=contains(
                has_entries(id=line1['id']),
                has_entries(id=line2['id']),
                has_entries(id=line3['id']),
            )
        ),
    )


@fixtures.user()
@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_user_to_multiple_lines_with_same_extension(
    user, extension, line1, line2
):
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
def test_associate_user_to_multiple_lines_with_different_extension(
    user, extension1, extension2, line1, line2
):
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
def test_associate_two_users_to_two_lines_with_same_extension(
    user1, user2, extension, line1, line2
):
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

        response = confd.users(user['id']).get()
        assert_that(
            response.item['lines'],
            contains(has_entries(id=line['id'])),
        )


@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_lines_to_user(user, line1, line2):
    response = confd.users(user['uuid']).lines.put(lines=[line2, line1])
    response.assert_updated()

    response = confd.users(user['uuid']).get()
    assert_that(
        response.item['lines'],
        contains(has_entries(id=line2['id']), has_entries(id=line1['id'])),
    )


@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_lines_to_swap_main_line(user, line1, line2):
    response = confd.users(user['uuid']).lines.put(lines=[line1, line2])
    response.assert_updated()

    response = confd.users(user['uuid']).get()
    assert_that(
        response.item['lines'],
        contains(has_entries(id=line1['id']), has_entries(id=line2['id'])),
    )

    response = confd.users(user['uuid']).lines.put(lines=[line2, line1])
    response.assert_updated()

    response = confd.users(user['uuid']).get()
    assert_that(
        response.item['lines'],
        contains(has_entries(id=line2['id']), has_entries(id=line1['id'])),
    )


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
    with a.user_line(first_user, line, check=False), a.user_line(
        second_user, line, check=False
    ):
        response = confd.users(second_user['id']).lines(line['id']).delete()
        response.assert_deleted()

        response = confd.users(first_user['id']).lines(line['id']).delete()
        response.assert_deleted()


@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.line_sip()
def test_dissociate_main_line_then_main_line_fallback_to_secondary(
    user, line1, line2, line3
):
    with a.user_line(user, line1, check=False), a.user_line(
        user, line2, check=False
    ), a.user_line(user, line3, check=False):
        response = confd.users(user['id']).get()
        assert_that(
            response.item,
            has_entries(
                lines=contains(
                    has_entries(id=line1['id']),
                    has_entries(id=line2['id']),
                    has_entries(id=line3['id']),
                )
            ),
        )

        confd.users(user['uuid']).lines(line1['id']).delete().assert_deleted()
        response = confd.users(user['uuid']).get()
        assert_that(
            response.item,
            has_entries(
                lines=contains(
                    has_entries(id=line2['id']),
                    has_entries(id=line3['id']),
                )
            ),
        )

        confd.users(user['uuid']).lines(line2['id']).delete().assert_deleted()
        response = confd.users(user['uuid']).get()
        assert_that(
            response.item,
            has_entries(lines=contains(has_entries(id=line3['id']))),
        )

        confd.users(user['uuid']).lines(line3['id']).delete().assert_deleted()
        response = confd.users(user['uuid']).get()
        assert_that(response.item, has_entries(lines=empty()))


@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
def test_dissociate_second_user_before_first(first_user, second_user, line):
    with a.user_line(first_user, line), a.user_line(second_user, line):
        response = confd.users(first_user['id']).lines(line['id']).delete()
        response.assert_match(400, secondary_user_regex)


@fixtures.user()
@fixtures.line_sip()
def test_dissociate_not_associated(user, line):
    response = confd.users(user['uuid']).lines(line['id']).delete()
    response.assert_deleted()


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(main_internal, sub_internal, main_user, sub_user):
    @fixtures.line_sip(context=main_internal, wazo_tenant=MAIN_TENANT)
    @fixtures.line_sip(context=sub_internal, wazo_tenant=SUB_TENANT)
    def aux(main_line, sub_line):
        response = (
            confd.users(sub_user['id'])
            .lines(main_line['id'])
            .delete(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Line'))

        response = (
            confd.users(main_user['id'])
            .lines(sub_line['id'])
            .delete(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('User'))

    aux()


@fixtures.user()
@fixtures.line_sip()
def test_get_users_relation(user, line):
    with a.user_line(user, line):
        response = confd.lines(line['id']).get()
        assert_that(
            response.item['users'],
            contains(
                has_entries(
                    uuid=user['uuid'],
                    firstname=user['firstname'],
                    lastname=user['lastname'],
                )
            ),
        )


@fixtures.user()
@fixtures.line()
@fixtures.sip()
def test_get_lines_relation(user, line, sip):
    with a.line_endpoint_sip(line, sip):
        with a.user_line(user, line):
            line = confd.lines(line['id']).get().item
            response = confd.users(user['id']).get()
            assert_that(
                response.item['lines'],
                contains(
                    has_entries(
                        id=line['id'],
                        name=line['name'],
                        endpoint_sip=line['endpoint_sip'],
                        endpoint_sccp=line['endpoint_sccp'],
                        endpoint_custom=line['endpoint_custom'],
                        extensions=line['extensions'],
                    )
                ),
            )


@fixtures.user()
@fixtures.line_sip()
def test_delete_user_when_user_and_line_associated(user, line):
    with a.user_line(user, line, check=False):
        response = confd.users(user['id']).delete()
        response.assert_deleted()


@fixtures.user()
@fixtures.line_sip()
def test_bus_events(user, line):
    url = confd.users(user['uuid']).lines(line['id'])
    headers = {
        'tenant_uuid': user['tenant_uuid'],
        f'user_uuid:{user["uuid"]}': True,
    }

    (s.check_event('user_line_associated', headers, url.put))
    (s.check_event('user_line_dissociated', headers, url.delete))
