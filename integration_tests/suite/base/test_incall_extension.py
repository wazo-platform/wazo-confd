# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    has_entries,
)

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    INCALL_CONTEXT,
    CONTEXT,
    MAIN_TENANT,
    SUB_TENANT,
)

FAKE_ID = 999999999


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_associate_errors(incall, extension):
    fake_incall = confd.incalls(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.incalls(incall['id']).extensions(FAKE_ID).put

    yield s.check_resource_not_found, fake_incall, 'Incall'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_dissociate_errors(incall, extension):
    fake_incall = confd.incalls(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.incalls(incall['id']).extensions(FAKE_ID).delete

    yield s.check_resource_not_found, fake_incall, 'Incall'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_associate(incall, extension):
    response = confd.incalls(incall['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_associate_already_associated(incall, extension):
    with a.incall_extension(incall, extension):
        response = confd.incalls(incall['id']).extensions(extension['id']).put()
        response.assert_updated()


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
@fixtures.extension(context=INCALL_CONTEXT)
def test_associate_multiple_extensions_to_incall(incall, extension1, extension2):
    with a.incall_extension(incall, extension1):
        response = confd.incalls(incall['id']).extensions(extension2['id']).put()
        response.assert_match(400, e.resource_associated('Incall', 'Extension'))


@fixtures.incall()
@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_associate_multiple_incalls_to_extension(incall1, incall2, extension):
    with a.incall_extension(incall1, extension):
        response = confd.incalls(incall2['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('Incall', 'Extension'))


@fixtures.incall()
@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_associate_when_user_already_associated(incall, user, line_sip, extension):
    with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
        response = confd.incalls(incall['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('user', 'Extension'))


@fixtures.incall()
@fixtures.extension()
def test_associate_when_not_incall_context(incall, extension):
    response = confd.incalls(incall['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.incall(wazo_tenant=MAIN_TENANT)
@fixtures.incall(wazo_tenant=SUB_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT, type='incall', name='sub-incall')
@fixtures.extension(context='sub-incall')
@fixtures.extension(context=INCALL_CONTEXT)
def test_associate_multi_tenant(main_incall, sub_incall, sub_ctx, sub_exten, main_exten):
    response = confd.incalls(sub_incall['id']).extensions(main_exten['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Extension'))

    response = confd.incalls(main_incall['id']).extensions(sub_exten['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Incall'))

    response = confd.incalls(main_incall['id']).extensions(sub_exten['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_dissociate(incall, extension):
    with a.incall_extension(incall, extension, check=False):
        response = confd.incalls(incall['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.incall(wazo_tenant=MAIN_TENANT)
@fixtures.incall(wazo_tenant=SUB_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT, type='incall', name='sub-incall')
@fixtures.extension(context='sub-incall')
@fixtures.extension(context=INCALL_CONTEXT)
def test_dissociate_multi_tenant(main_incall, sub_incall, sub_ctx, sub_exten, main_exten):
    response = confd.incalls(sub_incall['id']).extensions(main_exten['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Extension'))

    response = confd.incalls(main_incall['id']).extensions(sub_exten['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Incall'))


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_dissociate_not_associated(incall, extension):
    response = confd.incalls(incall['id']).extensions(extension['id']).delete()
    response.assert_deleted()


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_get_incall_relation(incall, extension):
    with a.incall_extension(incall, extension):
        response = confd.incalls(incall['id']).get()
        assert_that(
            response.item,
            has_entries(
                extensions=contains(has_entries(
                    id=extension['id'],
                    exten=extension['exten'],
                    context=extension['context'],
                ))
            )
        )


@fixtures.extension(context=INCALL_CONTEXT)
@fixtures.incall()
def test_get_extension_relation(extension, incall):
    with a.incall_extension(incall, extension):
        response = confd.extensions(extension['id']).get()
        assert_that(response.item, has_entries(incall=has_entries(id=incall['id'])))


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_edit_context_to_internal_when_associated(incall, extension):
    with a.incall_extension(incall, extension):
        response = confd.extensions(extension['id']).put(context=CONTEXT)
        response.assert_status(400)


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_delete_incall_when_incall_and_extension_associated(incall, extension):
    with a.incall_extension(incall, extension, check=False):
        response = confd.incalls(incall['id']).delete()
        response.assert_deleted()


def test_delete_extension_when_incall_and_extension_associated():
    # It is impossible to delete an extension while it associated to an object
    pass
