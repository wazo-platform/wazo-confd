# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    empty,
    has_entries,
    has_item,
    has_items,
)

from ..helpers import (
    scenarios as s,
    errors as e,
    associations as a,
    fixtures,
)
from ..helpers.config import (
    EXTEN_OUTSIDE_RANGE,
    INCALL_CONTEXT,
    MAIN_TENANT,
    SUB_TENANT,
)
from . import confd, db

FAKE_ID = 999999999


def test_associate_errors():
    with fixtures.line() as line, fixtures.extension() as extension:
        fake_line = confd.lines(FAKE_ID).extensions(extension['id']).put
        fake_extension = confd.lines(line['id']).extensions(FAKE_ID).put

        s.check_resource_not_found(fake_line, 'Line')
        s.check_resource_not_found(fake_extension, 'Extension')



def test_associate_multi_tenant():
    with fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal') as main_ctx, fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal') as sub_ctx, fixtures.line_sip(context='main-internal') as main_line, fixtures.line_sip(context='sub-internal') as sub_line, fixtures.extension(context='main-internal') as main_exten, fixtures.extension(context='sub-internal') as sub_exten:
        response = confd.lines(sub_line['id']).extensions(main_exten['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        response = confd.lines(main_line['id']).extensions(sub_exten['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Line'))

        response = confd.lines(main_line['id']).extensions(sub_exten['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate_errors():
    with fixtures.line() as line, fixtures.extension() as extension:
        fake_line = confd.lines(FAKE_ID).extensions(extension['id']).delete
        fake_extension = confd.lines(line['id']).extensions(FAKE_ID).delete

        s.check_resource_not_found(fake_line, 'Line')
        s.check_resource_not_found(fake_extension, 'Extension')



def test_dissociate_multi_tenant():
    with fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal') as main_ctx, fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal') as sub_ctx, fixtures.line_sip(context='main-internal') as main_line, fixtures.line_sip(context='sub-internal') as sub_line, fixtures.extension(context='main-internal') as main_exten, fixtures.extension(context='sub-internal') as sub_exten:
        url = confd.lines(sub_line['id']).extensions(main_exten['id'])
        response = url.delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        url = confd.lines(main_line['id']).extensions(sub_exten['id'])
        response = url.delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Line'))



def test_get_errors():
    fake_line = confd.lines(FAKE_ID).extensions.get
    fake_extension = confd.extensions(FAKE_ID).lines.get

    s.check_resource_not_found(fake_line, 'Line')
    s.check_resource_not_found(fake_extension, 'Extension')


def test_get_errors_deprecated():
    with fixtures.extension() as extension:
        fake_extension_deprecated = confd.extensions(FAKE_ID).line.get
        not_associated_extension_deprecated = confd.extensions(extension['id']).line.get

        s.check_resource_not_found(fake_extension_deprecated, 'Extension')
        s.check_resource_not_found(not_associated_extension_deprecated, 'LineExtension')



def test_get_associations_when_not_associated():
    with fixtures.line_sip() as line, fixtures.extension() as extension:
        response = confd.lines(line['id']).extensions.get()
        assert_that(response.items, empty())

        response = confd.extensions(extension['id']).lines.get()
        assert_that(response.items, empty())



def test_associate_deprecated():
    with fixtures.line_sip() as line, fixtures.extension() as extension:
        response = confd.lines(line['id']).extensions.post(extension_id=extension['id'])
        response.assert_created('lines', 'extensions')



def test_associate_line_and_internal_extension():
    with fixtures.line_sip() as line, fixtures.extension() as extension:
        response = confd.lines(line['id']).extensions(extension['id']).put()
        response.assert_updated()

        response = confd.lines(line['id']).extensions.get()
        assert_that(
            response.items,
            contains(
                has_entries(line_id=line['id'], extension_id=extension['id']),
            )
        )



def test_associate_extension_not_in_internal_context():
    with fixtures.extension(context=INCALL_CONTEXT) as extension, fixtures.line_sip() as line:
        response = confd.lines(line['id']).extensions(extension['id']).put()
        response.assert_status(400)



def test_associate_extension_to_one_line_multiple_users():
    with fixtures.extension() as extension, fixtures.line_sip() as line, fixtures.user() as first_user, fixtures.user() as second_user:
        with a.user_line(first_user, line), a.user_line(second_user, line):
            response = confd.lines(line['id']).extensions(extension['id']).put()
            response.assert_updated()


def test_associate_two_internal_extensions_to_same_line():
    with fixtures.extension() as first_extension, fixtures.extension() as second_extension, fixtures.line_sip() as line:
        response = confd.lines(line['id']).extensions(first_extension['id']).put()
        response.assert_updated()

        response = confd.lines(line['id']).extensions(second_extension['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Extension'))



def test_associate_multi_lines_to_extension():
    with fixtures.extension() as extension, fixtures.line_sip() as line1, fixtures.line_sip() as line2, fixtures.line_sip() as line3:
        response = confd.lines(line1['id']).extensions(extension['id']).put()
        response.assert_updated()

        response = confd.lines(line2['id']).extensions(extension['id']).put()
        response.assert_updated()

        response = confd.lines(line3['id']).extensions(extension['id']).put()
        response.assert_updated()



def test_associate_multi_lines_to_extension_with_same_user():
    with fixtures.user() as user, fixtures.extension() as extension, fixtures.line_sip() as line1, fixtures.line_sip() as line2:
        with a.user_line(user, line1), a.user_line(user, line2):
            response = confd.lines(line1['id']).extensions(extension['id']).put()
            response.assert_updated()

            response = confd.lines(line2['id']).extensions(extension['id']).put()
            response.assert_updated()


def test_associate_multi_lines_to_extension_with_different_user():
    with fixtures.user() as user1, fixtures.user() as user2, fixtures.extension() as exten, fixtures.line_sip() as line1, fixtures.line_sip() as line2:
        with a.user_line(user1, line1), a.user_line(user2, line2):
            response = confd.lines(line1['id']).extensions(exten['id']).put()
            response.assert_updated()

            response = confd.lines(line2['id']).extensions(exten['id']).put()
            response.assert_match(400, e.resource_associated('User', 'Line'))


def test_associate_multi_lines_to_multi_extensions_with_same_user():
    with fixtures.user() as user, fixtures.extension() as extension1, fixtures.extension() as extension2, fixtures.line_sip() as line1, fixtures.line_sip() as line2:
        with a.user_line(user, line1), a.user_line(user, line2):
            response = confd.lines(line1['id']).extensions(extension1['id']).put()
            response.assert_updated()

            response = confd.lines(line2['id']).extensions(extension2['id']).put()
            response.assert_updated()


def test_associate_line_to_extension_already_associated():
    with fixtures.extension() as extension, fixtures.line_sip() as line:
        with a.line_extension(line, extension):
            response = confd.lines(line['id']).extensions(extension['id']).put()
            response.assert_updated()


def test_associate_line_to_extension_already_associated_to_other_resource():
    with fixtures.line_sip() as line:
        with db.queries() as queries:
            queries.insert_queue(number='1234', tenant_uuid=MAIN_TENANT)

        extension_id = confd.extensions.get(exten='1234').items[0]['id']

        response = confd.lines(line['id']).extensions(extension_id).put()
        response.assert_match(400, e.resource_associated('Extension', 'queue'))


def test_associate_line_without_endpoint():
    with fixtures.line() as line, fixtures.extension() as extension:
        response = confd.lines(line['id']).extensions(extension['id']).put()
        response.assert_match(400, e.missing_association('Line', 'Endpoint'))



def test_associate_line_with_endpoint():
    with fixtures.line() as line, fixtures.sip() as sip, fixtures.extension() as extension:
        with a.line_endpoint_sip(line, sip, check=False):
            response = confd.lines(line['id']).extensions(extension['id']).put()
            response.assert_updated()
            response = confd.lines(line['id']).extensions.get()
            assert_that(
                response.items,
                contains(
                    has_entries(line_id=line['id'], extension_id=extension['id']),
                )
            )


def test_associate_when_exten_outside_range():
    with fixtures.line_sip() as line, fixtures.extension(exten=EXTEN_OUTSIDE_RANGE) as extension:
        response = confd.lines(line['id']).extensions(extension['id']).put()
        response.assert_status(400)



def test_associate_when_exten_pattern():
    with fixtures.line_sip() as line, fixtures.extension(exten='_9123') as extension:
        response = confd.lines(line['id']).extensions(extension['id']).put()
        response.assert_updated()



def test_dissociate_line_and_extension():
    with fixtures.line_sip() as line, fixtures.extension() as extension:
        with a.line_extension(line, extension, check=False):
            response = confd.lines(line['id']).extensions(extension['id']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.line_sip() as line, fixtures.extension() as extension:
        response = confd.lines(line['id']).extensions(extension['id']).delete()
        response.assert_deleted()



def test_delete_extension_associated_to_line():
    with fixtures.line_sip() as line, fixtures.extension() as extension:
        with a.line_extension(line, extension):
            response = confd.extensions(extension['id']).delete()
            response.assert_match(400, e.resource_associated('Extension', 'Line'))


def test_get_line_extension():
    with fixtures.line_sip() as line, fixtures.extension() as extension:
        expected = has_item(has_entries(line_id=line['id'], extension_id=extension['id']))

        with a.line_extension(line, extension):
            response = confd.lines(line['id']).extensions.get()
            assert_that(response.items, expected)

            response = confd.extensions(extension['id']).lines.get()
            assert_that(response.items, expected)



def test_get_multi_lines_extension():
    with fixtures.line_sip() as line1, fixtures.line_sip() as line2, fixtures.extension() as extension:
        with a.line_extension(line1, extension), a.line_extension(line2, extension):
            response = confd.extensions(extension['id']).lines.get()
            assert_that(
                response.items,
                has_items(
                    has_entries(line_id=line1['id'], extension_id=extension['id']),
                    has_entries(line_id=line2['id'], extension_id=extension['id']),
                )
            )


def test_dissociation():
    with fixtures.line_sip() as line, fixtures.extension() as extension:
        with a.line_extension(line, extension, check=False):
            confd.lines(line['id']).extensions(extension['id']).delete().assert_deleted()
            response = confd.lines(line['id']).extensions.get()
            assert_that(response.items, empty())


def test_edit_context_to_incall_when_associated():
    with fixtures.line_sip() as line, fixtures.extension() as extension:
        with a.line_extension(line, extension, check=True):
            response = confd.extensions(extension['id']).put(context=INCALL_CONTEXT)
            response.assert_status(400)


def test_get_extension_relation():
    with fixtures.line_sip() as line, fixtures.extension() as exten:
        with a.line_extension(line, exten):
            response = confd.lines(line['id']).get()
            assert_that(
                response.item['extensions'],
                contains(
                    has_entries(id=exten['id'], exten=exten['exten'], context=exten['context']),
                )
            )


def test_get_line_relation():
    with fixtures.line() as line, fixtures.sip() as sip, fixtures.extension() as extension:
        with a.line_endpoint_sip(line, sip):
            with a.line_extension(line, extension):
                line = confd.lines(line['id']).get().item
                response = confd.extensions(extension['id']).get()
                assert_that(
                    response.item['lines'],
                    contains(
                        has_entries(id=line['id'], name=line['name']),
                    )
                )
