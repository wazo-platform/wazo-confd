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
    OUTCALL_CONTEXT,
    CONTEXT,
    MAIN_TENANT,
    SUB_TENANT,
)

FAKE_ID = 999999999


def test_associate_errors():
    with fixtures.outcall() as outcall, fixtures.extension(context=OUTCALL_CONTEXT) as extension:
        fake_outcall = confd.outcalls(FAKE_ID).extensions(extension['id']).put
        fake_extension = confd.outcalls(outcall['id']).extensions(FAKE_ID).put

        s.check_resource_not_found(fake_outcall, 'Outcall')
        s.check_resource_not_found(fake_extension, 'Extension')

        url = confd.outcalls(outcall['id']).extensions(extension['id']).put
        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'caller_id', 123)
    s.check_bogus_field_returns_error(url, 'caller_id', True)
    s.check_bogus_field_returns_error(url, 'caller_id', {})
    s.check_bogus_field_returns_error(url, 'caller_id', [])
    s.check_bogus_field_returns_error(url, 'caller_id', s.random_string(81))
    s.check_bogus_field_returns_error(url, 'external_prefix', s.random_string(65))
    s.check_bogus_field_returns_error(url, 'external_prefix', 'invalid_regex')
    s.check_bogus_field_returns_error(url, 'external_prefix', True)
    s.check_bogus_field_returns_error(url, 'external_prefix', [])
    s.check_bogus_field_returns_error(url, 'external_prefix', {})
    s.check_bogus_field_returns_error(url, 'prefix', s.random_string(33))
    s.check_bogus_field_returns_error(url, 'prefix', 'invalid_regex')
    s.check_bogus_field_returns_error(url, 'prefix', True)
    s.check_bogus_field_returns_error(url, 'prefix', [])
    s.check_bogus_field_returns_error(url, 'prefix', {})
    s.check_bogus_field_returns_error(url, 'strip_digits', None)
    s.check_bogus_field_returns_error(url, 'strip_digits', 'string')
    s.check_bogus_field_returns_error(url, 'strip_digits', -1)
    s.check_bogus_field_returns_error(url, 'strip_digits', [])
    s.check_bogus_field_returns_error(url, 'strip_digits', {})


def test_dissociate_errors():
    with fixtures.outcall() as outcall, fixtures.extension(context=OUTCALL_CONTEXT) as extension:
        fake_outcall = confd.outcalls(FAKE_ID).extensions(extension['id']).delete
        fake_extension = confd.outcalls(outcall['id']).extensions(FAKE_ID).delete

        s.check_resource_not_found(fake_outcall, 'Outcall')
        s.check_resource_not_found(fake_extension, 'Extension')



def test_associate():
    with fixtures.outcall() as outcall, fixtures.extension(context=OUTCALL_CONTEXT) as extension:
        response = confd.outcalls(outcall['id']).extensions(extension['id']).put()
        response.assert_updated()



def test_associate_with_all_parameters():
    with fixtures.outcall() as outcall, fixtures.extension(context=OUTCALL_CONTEXT) as extension:
        parameters = {'caller_id': 'CallerID',
                      'external_prefix': '418',
                      'prefix': '514',
                      'strip_digits': 5}
        response = confd.outcalls(outcall['id']).extensions(extension['id']).put(parameters)
        response.assert_updated()



def test_associate_already_associated():
    with fixtures.outcall() as outcall, fixtures.extension(context=OUTCALL_CONTEXT) as extension:
        with a.outcall_extension(outcall, extension):
            response = confd.outcalls(outcall['id']).extensions(extension['id']).put(prefix='123')
            response.assert_updated()


def test_associate_multiple_extensions_to_outcall():
    with fixtures.outcall() as outcall, fixtures.extension(context=OUTCALL_CONTEXT) as extension1, fixtures.extension(context=OUTCALL_CONTEXT) as extension2:
        with a.outcall_extension(outcall, extension1):
            response = confd.outcalls(outcall['id']).extensions(extension2['id']).put()
            response.assert_updated()


def test_associate_multiple_outcalls_to_extension():
    with fixtures.outcall() as outcall1, fixtures.outcall() as outcall2, fixtures.extension(context=OUTCALL_CONTEXT) as extension:
        with a.outcall_extension(outcall1, extension):
            response = confd.outcalls(outcall2['id']).extensions(extension['id']).put()
            response.assert_match(400, e.resource_associated('outcall', 'Extension'))


def test_associate_when_user_already_associated():
    with fixtures.outcall() as outcall, fixtures.user() as user, fixtures.line_sip() as line_sip, fixtures.extension() as extension:
        with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
            response = confd.outcalls(outcall['id']).extensions(extension['id']).put()
            response.assert_match(400, e.resource_associated('user', 'Extension'))


def test_associate_when_not_outcall_context():
    with fixtures.outcall() as outcall, fixtures.extension() as extension:
        response = confd.outcalls(outcall['id']).extensions(extension['id']).put()
        response.assert_status(400)



def test_associate_multi_tenant():
    with fixtures.outcall(wazo_tenant=MAIN_TENANT) as main_outcall, fixtures.outcall(wazo_tenant=SUB_TENANT) as sub_outcall, fixtures.context(wazo_tenant=SUB_TENANT, type='outcall', name='sub-outcall') as sub_ctx, fixtures.extension(context='sub-outcall') as sub_exten, fixtures.extension(context=OUTCALL_CONTEXT) as main_exten:
        response = confd.outcalls(sub_outcall['id']).extensions(main_exten['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        response = confd.outcalls(main_outcall['id']).extensions(sub_exten['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Outcall'))

        response = confd.outcalls(main_outcall['id']).extensions(sub_exten['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate_multi_tenant():
    with fixtures.outcall(wazo_tenant=MAIN_TENANT) as main_outcall, fixtures.outcall(wazo_tenant=SUB_TENANT) as sub_outcall, fixtures.context(wazo_tenant=SUB_TENANT, type='outcall', name='sub-outcall') as sub_ctx, fixtures.extension(context='sub-outcall') as sub_exten, fixtures.extension(context=OUTCALL_CONTEXT) as main_exten:
        response = confd.outcalls(sub_outcall['id']).extensions(main_exten['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        response = confd.outcalls(main_outcall['id']).extensions(sub_exten['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Outcall'))



def test_dissociate():
    with fixtures.outcall() as outcall, fixtures.extension(context=OUTCALL_CONTEXT) as extension:
        with a.outcall_extension(outcall, extension, check=False):
            response = confd.outcalls(outcall['id']).extensions(extension['id']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.outcall() as outcall, fixtures.extension(context=OUTCALL_CONTEXT) as extension:
        response = confd.outcalls(outcall['id']).extensions(extension['id']).delete()
        response.assert_deleted()



def test_get_outcall_relations():
    with fixtures.outcall() as outcall, fixtures.extension(context=OUTCALL_CONTEXT) as extension:
        with a.outcall_extension(outcall, extension,
                                 external_prefix='123', prefix='456', strip_digits=2, caller_id='toto'):
            response = confd.outcalls(outcall['id']).get()
            assert_that(
                response.item,
                has_entries(
                    extensions=contains(
                        has_entries(
                            id=extension['id'],
                            exten=extension['exten'],
                            context=extension['context'],
                            external_prefix='123',
                            prefix='456',
                            strip_digits=2,
                            caller_id='toto'
                        )
                    )
                )
            )


def test_get_extension_relations():
    with fixtures.outcall() as outcall, fixtures.extension(context=OUTCALL_CONTEXT) as extension:
        with a.outcall_extension(outcall, extension):
            response = confd.extensions(extension['id']).get()
            assert_that(
                response.item,
                has_entries(
                    outcall=has_entries(id=outcall['id'], name=outcall['name'])
                )
            )


def test_edit_context_to_internal_when_associated():
    with fixtures.outcall() as outcall, fixtures.extension(context=OUTCALL_CONTEXT) as extension:
        with a.outcall_extension(outcall, extension):
            response = confd.extensions(extension['id']).put(context=CONTEXT)
            response.assert_status(400)


def test_delete_outcall_when_outcall_and_extension_associated():
    with fixtures.outcall() as outcall, fixtures.extension(context=OUTCALL_CONTEXT) as extension:
        with a.outcall_extension(outcall, extension, check=False):
            response = confd.outcalls(outcall['id']).delete()
            response.assert_deleted()


def test_delete_extension_when_outcall_and_extension_associated():
    # It is impossible to delete an extension while it associated to an object
    pass
