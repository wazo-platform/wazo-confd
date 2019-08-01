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


def test_associate_errors():
    with fixtures.incall() as incall, fixtures.extension(context=INCALL_CONTEXT) as extension:
        fake_incall = confd.incalls(FAKE_ID).extensions(extension['id']).put
        fake_extension = confd.incalls(incall['id']).extensions(FAKE_ID).put

        s.check_resource_not_found(fake_incall, 'Incall')
        s.check_resource_not_found(fake_extension, 'Extension')



def test_dissociate_errors():
    with fixtures.incall() as incall, fixtures.extension(context=INCALL_CONTEXT) as extension:
        fake_incall = confd.incalls(FAKE_ID).extensions(extension['id']).delete
        fake_extension = confd.incalls(incall['id']).extensions(FAKE_ID).delete

        s.check_resource_not_found(fake_incall, 'Incall')
        s.check_resource_not_found(fake_extension, 'Extension')



def test_associate():
    with fixtures.incall() as incall, fixtures.extension(context=INCALL_CONTEXT) as extension:
        response = confd.incalls(incall['id']).extensions(extension['id']).put()
        response.assert_updated()



def test_associate_already_associated():
    with fixtures.incall() as incall, fixtures.extension(context=INCALL_CONTEXT) as extension:
        with a.incall_extension(incall, extension):
            response = confd.incalls(incall['id']).extensions(extension['id']).put()
            response.assert_updated()


def test_associate_multiple_extensions_to_incall():
    with fixtures.incall() as incall, fixtures.extension(context=INCALL_CONTEXT) as extension1, fixtures.extension(context=INCALL_CONTEXT) as extension2:
        with a.incall_extension(incall, extension1):
            response = confd.incalls(incall['id']).extensions(extension2['id']).put()
            response.assert_match(400, e.resource_associated('Incall', 'Extension'))


def test_associate_multiple_incalls_to_extension():
    with fixtures.incall() as incall1, fixtures.incall() as incall2, fixtures.extension(context=INCALL_CONTEXT) as extension:
        with a.incall_extension(incall1, extension):
            response = confd.incalls(incall2['id']).extensions(extension['id']).put()
            response.assert_match(400, e.resource_associated('Incall', 'Extension'))


def test_associate_when_user_already_associated():
    with fixtures.incall() as incall, fixtures.user() as user, fixtures.line_sip() as line_sip, fixtures.extension() as extension:
        with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
            response = confd.incalls(incall['id']).extensions(extension['id']).put()
            response.assert_match(400, e.resource_associated('user', 'Extension'))


def test_associate_when_not_incall_context():
    with fixtures.incall() as incall, fixtures.extension() as extension:
        response = confd.incalls(incall['id']).extensions(extension['id']).put()
        response.assert_status(400)



def test_associate_multi_tenant():
    with fixtures.incall(wazo_tenant=MAIN_TENANT) as main_incall, fixtures.incall(wazo_tenant=SUB_TENANT) as sub_incall, fixtures.context(wazo_tenant=SUB_TENANT, type='incall', name='sub-incall') as sub_ctx, fixtures.extension(context='sub-incall') as sub_exten, fixtures.extension(context=INCALL_CONTEXT) as main_exten:
        response = confd.incalls(sub_incall['id']).extensions(main_exten['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        response = confd.incalls(main_incall['id']).extensions(sub_exten['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Incall'))

        response = confd.incalls(main_incall['id']).extensions(sub_exten['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.incall() as incall, fixtures.extension(context=INCALL_CONTEXT) as extension:
        with a.incall_extension(incall, extension, check=False):
            response = confd.incalls(incall['id']).extensions(extension['id']).delete()
            response.assert_deleted()


def test_dissociate_multi_tenant():
    with fixtures.incall(wazo_tenant=MAIN_TENANT) as main_incall, fixtures.incall(wazo_tenant=SUB_TENANT) as sub_incall, fixtures.context(wazo_tenant=SUB_TENANT, type='incall', name='sub-incall') as sub_ctx, fixtures.extension(context='sub-incall') as sub_exten, fixtures.extension(context=INCALL_CONTEXT) as main_exten:
        response = confd.incalls(sub_incall['id']).extensions(main_exten['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        response = confd.incalls(main_incall['id']).extensions(sub_exten['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Incall'))



def test_dissociate_not_associated():
    with fixtures.incall() as incall, fixtures.extension(context=INCALL_CONTEXT) as extension:
        response = confd.incalls(incall['id']).extensions(extension['id']).delete()
        response.assert_deleted()



def test_get_incall_relation():
    with fixtures.incall() as incall, fixtures.extension(context=INCALL_CONTEXT) as extension:
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


def test_get_extension_relation():
    with fixtures.extension(context=INCALL_CONTEXT) as extension, fixtures.incall() as incall:
        with a.incall_extension(incall, extension):
            response = confd.extensions(extension['id']).get()
            assert_that(response.item, has_entries(incall=has_entries(id=incall['id'])))


def test_edit_context_to_internal_when_associated():
    with fixtures.incall() as incall, fixtures.extension(context=INCALL_CONTEXT) as extension:
        with a.incall_extension(incall, extension):
            response = confd.extensions(extension['id']).put(context=CONTEXT)
            response.assert_status(400)


def test_delete_incall_when_incall_and_extension_associated():
    with fixtures.incall() as incall, fixtures.extension(context=INCALL_CONTEXT) as extension:
        with a.incall_extension(incall, extension, check=False):
            response = confd.incalls(incall['id']).delete()
            response.assert_deleted()


def test_delete_extension_when_incall_and_extension_associated():
    # It is impossible to delete an extension while it associated to an object
    pass
