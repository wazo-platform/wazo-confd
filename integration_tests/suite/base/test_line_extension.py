# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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


@fixtures.line()
@fixtures.extension()
def test_associate_errors(line, extension):
    fake_line = confd.lines(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.lines(line['id']).extensions(FAKE_ID).put

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.line_sip(context='main-internal')
@fixtures.line_sip(context='sub-internal')
@fixtures.extension(context='main-internal')
@fixtures.extension(context='sub-internal')
def test_associate_multi_tenant(main_ctx, sub_ctx, main_line, sub_line, main_exten, sub_exten):
    response = confd.lines(sub_line['id']).extensions(main_exten['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Extension'))

    response = confd.lines(main_line['id']).extensions(sub_exten['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Line'))

    response = confd.lines(main_line['id']).extensions(sub_exten['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())


@fixtures.line()
@fixtures.extension()
def test_dissociate_errors(line, extension):
    fake_line = confd.lines(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.lines(line['id']).extensions(FAKE_ID).delete

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.line_sip(context='main-internal')
@fixtures.line_sip(context='sub-internal')
@fixtures.extension(context='main-internal')
@fixtures.extension(context='sub-internal')
def test_dissociate_multi_tenant(main_ctx, sub_ctx, main_line, sub_line, main_exten, sub_exten):
    response = confd.lines(sub_line['id']).extensions(main_exten['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Extension'))

    response = confd.lines(main_line['id']).extensions(sub_exten['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Line'))


def test_get_errors():
    fake_line = confd.lines(FAKE_ID).extensions.get
    fake_extension = confd.extensions(FAKE_ID).lines.get

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.extension()
def test_get_errors_deprecated(extension):
    fake_extension_deprecated = confd.extensions(FAKE_ID).line.get
    not_associated_extension_deprecated = confd.extensions(extension['id']).line.get

    yield s.check_resource_not_found, fake_extension_deprecated, 'Extension'
    yield s.check_resource_not_found, not_associated_extension_deprecated, 'LineExtension'


@fixtures.line_sip()
@fixtures.extension()
def test_get_associations_when_not_associated(line, extension):
    response = confd.lines(line['id']).extensions.get()
    assert_that(response.items, empty())

    response = confd.extensions(extension['id']).lines.get()
    assert_that(response.items, empty())


@fixtures.line_sip()
@fixtures.extension()
def test_associate_deprecated(line, extension):
    response = confd.lines(line['id']).extensions.post(extension_id=extension['id'])
    response.assert_created('lines', 'extensions')


@fixtures.line_sip()
@fixtures.extension()
def test_associate_line_and_internal_extension(line, extension):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_updated()

    response = confd.lines(line['id']).extensions.get()
    assert_that(response.items, contains(has_entries({'line_id': line['id'],
                                                      'extension_id': extension['id']})))


@fixtures.extension(context=INCALL_CONTEXT)
@fixtures.line_sip()
def test_associate_extension_not_in_internal_context(extension, line):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.extension()
@fixtures.line_sip()
@fixtures.user()
@fixtures.user()
def test_associate_extension_to_one_line_multiple_users(extension, line, first_user, second_user):
    with a.user_line(first_user, line), a.user_line(second_user, line):
        response = confd.lines(line['id']).extensions(extension['id']).put()
        response.assert_updated()


@fixtures.extension()
@fixtures.extension()
@fixtures.line_sip()
def test_associate_two_internal_extensions_to_same_line(first_extension, second_extension, line):
    response = confd.lines(line['id']).extensions(first_extension['id']).put()
    response.assert_updated()

    response = confd.lines(line['id']).extensions(second_extension['id']).put()
    response.assert_match(400, e.resource_associated('Line', 'Extension'))


@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multi_lines_to_extension(extension, line1, line2, line3):
    response = confd.lines(line1['id']).extensions(extension['id']).put()
    response.assert_updated()

    response = confd.lines(line2['id']).extensions(extension['id']).put()
    response.assert_updated()

    response = confd.lines(line3['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.user()
@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multi_lines_to_extension_with_same_user(user, extension, line1, line2):
    with a.user_line(user, line1), a.user_line(user, line2):
        response = confd.lines(line1['id']).extensions(extension['id']).put()
        response.assert_updated()

        response = confd.lines(line2['id']).extensions(extension['id']).put()
        response.assert_updated()


@fixtures.user()
@fixtures.user()
@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multi_lines_to_extension_with_different_user(user1, user2, extension, line1, line2):
    with a.user_line(user1, line1), a.user_line(user2, line2):
        response = confd.lines(line1['id']).extensions(extension['id']).put()
        response.assert_updated()

        response = confd.lines(line2['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('User', 'Line'))


@fixtures.user()
@fixtures.extension()
@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multi_lines_to_multi_extensions_with_same_user(user, extension1, extension2, line1, line2):
    with a.user_line(user, line1), a.user_line(user, line2):
        response = confd.lines(line1['id']).extensions(extension1['id']).put()
        response.assert_updated()

        response = confd.lines(line2['id']).extensions(extension2['id']).put()
        response.assert_updated()


@fixtures.extension()
@fixtures.line_sip()
def test_associate_line_to_extension_already_associated(extension, line):
    with a.line_extension(line, extension):
        response = confd.lines(line['id']).extensions(extension['id']).put()
        response.assert_updated()


@fixtures.line_sip()
def test_associate_line_to_extension_already_associated_to_other_resource(line):
    with db.queries() as queries:
        queries.insert_queue(number='1234')

    extension_id = confd.extensions.get(exten='1234').items[0]['id']

    response = confd.lines(line['id']).extensions(extension_id).put()
    response.assert_match(400, e.resource_associated('Extension', 'queue'))


@fixtures.line()
@fixtures.extension()
def test_associate_line_without_endpoint(line, extension):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_match(400, e.missing_association('Line', 'Endpoint'))


@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_associate_line_with_endpoint(line, sip, extension):
    with a.line_endpoint_sip(line, sip, check=False):
        response = confd.lines(line['id']).extensions(extension['id']).put()
        response.assert_updated()
        response = confd.lines(line['id']).extensions.get()
        assert_that(response.items, contains(has_entries({'line_id': line['id'],
                                                          'extension_id': extension['id']})))


@fixtures.line_sip()
@fixtures.extension(exten=EXTEN_OUTSIDE_RANGE)
def test_associate_when_exten_outside_range(line, extension):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.line_sip()
@fixtures.extension(exten='_9123')
def test_associate_when_exten_pattern(line, extension):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.line_sip()
@fixtures.extension()
def test_dissociate_line_and_extension(line, extension):
    with a.line_extension(line, extension, check=False):
        response = confd.lines(line['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.line_sip()
@fixtures.extension()
def test_dissociate_not_associated(line, extension):
    response = confd.lines(line['id']).extensions(extension['id']).delete()
    response.assert_deleted()


@fixtures.line_sip()
@fixtures.extension()
def test_delete_extension_associated_to_line(line, extension):
    with a.line_extension(line, extension):
        response = confd.extensions(extension['id']).delete()
        response.assert_match(400, e.resource_associated('Extension', 'Line'))


@fixtures.line_sip()
@fixtures.extension()
def test_get_line_extension(line, extension):
    expected = has_item(has_entries(line_id=line['id'],
                                    extension_id=extension['id']))

    with a.line_extension(line, extension):
        response = confd.lines(line['id']).extensions.get()
        assert_that(response.items, expected)

        response = confd.extensions(extension['id']).lines.get()
        assert_that(response.items, expected)


@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.extension()
def test_get_multi_lines_extension(line1, line2, extension):
    expected = has_items(has_entries(line_id=line1['id'],
                                     extension_id=extension['id']),
                         has_entries(line_id=line2['id'],
                                     extension_id=extension['id']))

    with a.line_extension(line1, extension), a.line_extension(line2, extension):
        response = confd.extensions(extension['id']).lines.get()
        assert_that(response.items, expected)


@fixtures.line_sip()
@fixtures.extension()
def test_dissociation(line, extension):
    with a.line_extension(line, extension, check=False):
        confd.lines(line['id']).extensions(extension['id']).delete().assert_deleted()
        response = confd.lines(line['id']).extensions.get()
        assert_that(response.items, empty())


@fixtures.line_sip()
@fixtures.extension()
def test_edit_context_to_incall_when_associated(line, extension):
    with a.line_extension(line, extension, check=True):
        response = confd.extensions(extension['id']).put(context=INCALL_CONTEXT)
        response.assert_status(400)


@fixtures.line_sip()
@fixtures.extension()
def test_get_extension_relation(line, extension):
    expected = has_entries(
        extensions=contains(has_entries(id=extension['id'],
                                        exten=extension['exten'],
                                        context=extension['context']))
    )

    with a.line_extension(line, extension):
        response = confd.lines(line['id']).get()
        assert_that(response.item, expected)


@fixtures.line_sip()
@fixtures.extension()
def test_get_line_relation(line, extension):
    expected = has_entries(
        lines=contains(has_entries(id=line['id']))
    )

    with a.line_extension(line, extension):
        response = confd.extensions(extension['id']).get()
        assert_that(response.item, expected)
