# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains, has_entries

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import (
    EXTEN_OUTSIDE_RANGE,
    INCALL_CONTEXT,
    MAIN_TENANT,
    SUB_TENANT,
    gen_group_exten,
)
from . import confd

FAKE_ID = 999999999


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
def test_associate_errors(extension, group):
    fake_group = confd.groups(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.groups(group['id']).extensions(FAKE_ID).put

    s.check_resource_not_found(fake_group, 'Group')
    s.check_resource_not_found(fake_extension, 'Extension')

    fake_extension = confd.groups(group['uuid']).extensions(FAKE_ID).put

    s.check_resource_not_found(fake_extension, 'Extension')


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
def test_dissociate_errors(extension, group):
    fake_group = confd.groups(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.groups(group['id']).extensions(FAKE_ID).delete

    s.check_resource_not_found(fake_group, 'Group')
    s.check_resource_not_found(fake_extension, 'Extension')

    fake_extension = confd.groups(group['uuid']).extensions(FAKE_ID).delete

    s.check_resource_not_found(fake_extension, 'Extension')


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
def test_associate(extension, group):
    response = confd.groups(group['uuid']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
def test_associate_by_id(extension, group):
    response = confd.groups(group['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
def test_associate_already_associated(extension, group):
    with a.group_extension(group, extension):
        response = confd.groups(group['uuid']).extensions(extension['id']).put()
        response.assert_updated()


@fixtures.extension(exten=gen_group_exten())
@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
def test_associate_multiple_extensions_to_group(extension1, extension2, group):
    with a.group_extension(group, extension1):
        response = confd.groups(group['uuid']).extensions(extension2['id']).put()
        response.assert_match(400, e.resource_associated('Group', 'Extension'))


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
@fixtures.group()
def test_associate_multiple_groups_to_extension(extension, group1, group2):
    with a.group_extension(group1, extension):
        response = confd.groups(group2['uuid']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('Group', 'Extension'))


@fixtures.extension()
@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_associate_when_user_already_associated(extension, group, user, line_sip):
    with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
        response = confd.groups(group['uuid']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('user', 'Extension'))


@fixtures.extension(exten=gen_group_exten(), context=INCALL_CONTEXT)
@fixtures.group()
def test_associate_when_not_internal_context(extension, group):
    response = confd.groups(group['uuid']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.extension(exten=EXTEN_OUTSIDE_RANGE)
@fixtures.group()
def test_associate_when_exten_outside_range(extension, group):
    response = confd.groups(group['uuid']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.extension(exten='_5678')
@fixtures.group()
def test_associate_when_exten_pattern(extension, group):
    response = confd.groups(group['uuid']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
@fixtures.context(wazo_tenant=MAIN_TENANT, label='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, label='sub-internal')
def test_associate_multi_tenant(main_group, sub_group, main_ctx, sub_ctx):
    @fixtures.extension(context=main_ctx['name'], exten=gen_group_exten())
    @fixtures.extension(context=sub_ctx['name'], exten=gen_group_exten())
    def aux(main_exten, sub_exten):
        response = (
            confd.groups(sub_group['uuid'])
            .extensions(main_exten['id'])
            .put(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Extension'))

        response = (
            confd.groups(main_group['uuid'])
            .extensions(sub_exten['id'])
            .put(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Group'))

        response = (
            confd.groups(main_group['uuid'])
            .extensions(sub_exten['id'])
            .put(wazo_tenant=MAIN_TENANT)
        )
        response.assert_match(400, e.different_tenant())

    aux()


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
def test_dissociate(extension, group):
    with a.group_extension(group, extension, check=False):
        response = confd.groups(group['uuid']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
def test_dissociate_by_id(extension, group):
    with a.group_extension(group, extension, check=False):
        response = confd.groups(group['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
def test_dissociate_not_associated(extension, group):
    response = confd.groups(group['uuid']).extensions(extension['id']).delete()
    response.assert_deleted()


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
@fixtures.context(wazo_tenant=MAIN_TENANT, label='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, label='sub-internal')
def test_dissociate_multi_tenant(main_group, sub_group, main_ctx, sub_ctx):
    @fixtures.extension(context=main_ctx['name'], exten=gen_group_exten())
    @fixtures.extension(context=sub_ctx['name'], exten=gen_group_exten())
    def aux(main_exten, sub_exten):
        response = (
            confd.groups(sub_group['uuid'])
            .extensions(main_exten['id'])
            .delete(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Extension'))

        response = (
            confd.groups(main_group['uuid'])
            .extensions(sub_exten['id'])
            .delete(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Group'))

    aux()


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
def test_get_group_relation(extension, group):
    with a.group_extension(group, extension):
        response = confd.groups(group['uuid']).get()
        assert_that(
            response.item,
            has_entries(
                extensions=contains(
                    has_entries(
                        id=extension['id'],
                        exten=extension['exten'],
                        context=extension['context'],
                    )
                )
            ),
        )


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
def test_get_extension_relation(extension, group):
    with a.group_extension(group, extension):
        response = confd.extensions(extension['id']).get()
        assert_that(
            response.item,
            has_entries(
                group=has_entries(
                    uuid=group['uuid'],
                    id=group['id'],
                    name=group['name'],
                )
            ),
        )


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
def test_edit_context_to_incall_when_associated(extension, group):
    with a.group_extension(group, extension):
        response = confd.extensions(extension['id']).put(context=INCALL_CONTEXT)
        response.assert_status(400)


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
def test_delete_group_when_group_and_extension_associated(extension, group):
    with a.group_extension(group, extension, check=False):
        response = confd.groups(group['uuid']).delete()
        response.assert_deleted()


def test_delete_extension_when_group_and_extension_associated():
    # It is impossible to delete an extension while it associated to an object
    pass


@fixtures.extension(exten=gen_group_exten())
@fixtures.group()
def test_bus_events(extension, group):
    url = confd.groups(group['uuid']).extensions(extension['id'])
    headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event('group_extension_associated', headers, url.put)
    s.check_event('group_extension_dissociated', headers, url.delete)
