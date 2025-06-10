# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    greater_than,
    has_entries,
    none,
)

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import helpers as h
from ..helpers import scenarios as s
from ..helpers.config import (
    CONTEXT,
    EXTEN_OUTSIDE_RANGE,
    EXTEN_QUEUE_RANGE,
    INCALL_CONTEXT,
    MAIN_TENANT,
    SUB_TENANT,
)
from . import confd
from .test_extensions import error_checks

FAKE_ID = 999999999


@fixtures.line()
@fixtures.extension()
def test_associate_errors(line, extension):
    fake_line = confd.lines(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.lines(line['id']).extensions(FAKE_ID).put

    s.check_resource_not_found(fake_line, 'Line')
    s.check_resource_not_found(fake_extension, 'Extension')


@fixtures.context(wazo_tenant=MAIN_TENANT, label='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, label='sub-internal')
def test_associate_multi_tenant(main_ctx, sub_ctx):
    @fixtures.extension(context=main_ctx['name'])
    @fixtures.extension(context=sub_ctx['name'])
    @fixtures.line_sip(context=main_ctx, wazo_tenant=MAIN_TENANT)
    @fixtures.line_sip(context=sub_ctx, wazo_tenant=SUB_TENANT)
    def aux(main_exten, sub_exten, main_line, sub_line):
        response = (
            confd.lines(sub_line['id'])
            .extensions(main_exten['id'])
            .put(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Extension'))

        response = (
            confd.lines(main_line['id'])
            .extensions(sub_exten['id'])
            .put(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Line'))

        response = (
            confd.lines(main_line['id'])
            .extensions(sub_exten['id'])
            .put(wazo_tenant=MAIN_TENANT)
        )
        response.assert_match(400, e.different_tenant())

    aux()


@fixtures.line()
@fixtures.extension()
def test_dissociate_errors(line, extension):
    fake_line = confd.lines(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.lines(line['id']).extensions(FAKE_ID).delete

    s.check_resource_not_found(fake_line, 'Line')
    s.check_resource_not_found(fake_extension, 'Extension')


@fixtures.context(wazo_tenant=MAIN_TENANT, label='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, label='sub-internal')
def test_dissociate_multi_tenant(main_ctx, sub_ctx):
    @fixtures.extension(context=main_ctx['name'])
    @fixtures.extension(context=sub_ctx['name'])
    @fixtures.line_sip(context=main_ctx, wazo_tenant=MAIN_TENANT)
    @fixtures.line_sip(context=sub_ctx, wazo_tenant=SUB_TENANT)
    def aux(main_exten, sub_exten, main_line, sub_line):
        url = confd.lines(sub_line['id']).extensions(main_exten['id'])
        response = url.delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        url = confd.lines(main_line['id']).extensions(sub_exten['id'])
        response = url.delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Line'))

    aux()


@fixtures.line_sip()
@fixtures.extension()
def test_associate_line_and_internal_extension(line, extension):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_updated()

    response = confd.lines(line['id']).get()
    assert_that(
        response.item['extensions'], contains(has_entries({'id': extension['id']}))
    )


@fixtures.line_sip()
def test_associate_line_and_create_extension(line):
    exten = h.extension.find_available_exten(CONTEXT)

    response = confd.lines(line['id']).extensions.post(exten=exten, context=CONTEXT)
    response.assert_created('extensions')
    extension = response.item

    try:
        response = confd.lines(line['id']).get()
        assert_that(
            response.item['extensions'], contains(has_entries({'id': extension['id']}))
        )
    finally:
        confd.lines(line['id']).extensions(extension['id']).delete()
        confd.extensions(extension['id']).delete().assert_deleted()


def test_associate_line_and_create_extension_unknown_line():
    exten = h.extension.find_available_exten(CONTEXT)

    response = confd.lines(FAKE_ID).extensions.post(exten=exten, context=CONTEXT)
    response.assert_match(404, e.not_found(resource='Line'))


@fixtures.line_sip()
def test_extension_creation_error(line):
    url = confd.lines(line['id']).extensions.post
    error_checks(url)


@fixtures.context(label='sub_ctx', wazo_tenant=SUB_TENANT)
def test_extension_create_multi_tenant(context):
    @fixtures.line_sip(context={'name': context['name']}, wazo_tenant=SUB_TENANT)
    @fixtures.line_sip(context={'name': context['name']}, wazo_tenant=SUB_TENANT)
    @fixtures.line_sip()
    def aux(line_one, line_two, line_three):
        response = confd.lines(line_one['id']).extensions.post(
            exten='1000',
            context=context['name'],
            wazo_tenant=SUB_TENANT,
        )
        response.assert_created()
        extension = response.item
        try:
            assert_that(extension['tenant_uuid'], equal_to(SUB_TENANT))
        finally:
            confd.lines(line_one['id']).extensions(extension['id']).delete()
            confd.extensions(extension['id']).delete().assert_deleted()

        response = confd.lines(line_two['id']).extensions.post(
            exten=h.extension.find_available_exten(CONTEXT),
            context=CONTEXT,
        )
        response.assert_match(400, e.different_tenant())

        response = confd.lines(line_three['id']).extensions.post(
            exten='1001',
            context=context['name'],
            wazo_tenant=SUB_TENANT,
        )
        response.assert_match(404, e.not_found('Line'))

    aux()


@fixtures.extension(context=INCALL_CONTEXT)
@fixtures.line_sip()
def test_associate_extension_not_in_internal_context(extension, line):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.extension()
@fixtures.line_sip()
@fixtures.user()
@fixtures.user()
def test_associate_extension_to_one_line_multiple_users(
    extension, line, first_user, second_user
):
    with a.user_line(first_user, line), a.user_line(second_user, line):
        response = confd.lines(line['id']).extensions(extension['id']).put()
        response.assert_updated()


@fixtures.extension()
@fixtures.extension()
@fixtures.line_sip()
def test_associate_two_internal_extensions_to_same_line(
    first_extension, second_extension, line
):
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
def test_associate_multi_lines_to_extension_with_same_user(
    user, extension, line1, line2
):
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
def test_associate_multi_lines_to_extension_with_different_user(
    user1, user2, exten, line1, line2
):
    with a.user_line(user1, line1), a.user_line(user2, line2):
        response = confd.lines(line1['id']).extensions(exten['id']).put()
        response.assert_updated()

        response = confd.lines(line2['id']).extensions(exten['id']).put()
        response.assert_match(400, e.resource_associated('User', 'Line'))


@fixtures.user()
@fixtures.extension()
@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multi_lines_to_multi_extensions_with_same_user(
    user, extension1, extension2, line1, line2
):
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


@fixtures.extension(exten_range=EXTEN_QUEUE_RANGE)
@fixtures.queue()
@fixtures.line_sip()
def test_associate_line_to_extension_already_associated_to_other_resource(
    extension, queue, line
):
    with a.queue_extension(queue, extension):
        response = confd.lines(line['id']).extensions(extension['id']).put()
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
        response = confd.lines(line['id']).get()
        assert_that(
            response.item['extensions'],
            contains(has_entries({'id': extension['id']})),
        )


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
    with a.line_extension(line, extension, check=False):
        response = confd.extensions(extension['id']).delete()
        response.assert_status(400)


@fixtures.line_sip()
@fixtures.extension()
def test_delete_line_associated_to_extension(line, extension):
    with a.line_extension(line, extension, check=False):
        response = confd.lines(line['id']).delete()
        response.assert_deleted()


@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.extension()
def test_get_multi_lines_extension(line1, line2, extension):
    with a.line_extension(line1, extension), a.line_extension(line2, extension):
        response = confd.extensions(extension['id']).get()
        assert_that(
            response.item,
            has_entries(
                lines=contains_inanyorder(
                    has_entries({'id': line1['id']}),
                    has_entries({'id': line2['id']}),
                ),
            ),
        )


@fixtures.line_sip()
@fixtures.extension()
def test_dissociation(line, extension):
    with a.line_extension(line, extension, check=False):
        confd.lines(line['id']).extensions(extension['id']).delete().assert_deleted()
        response = confd.lines(line['id']).get()
        assert_that(response.item['extensions'], empty())


@fixtures.line_sip()
@fixtures.extension()
def test_edit_context_to_incall_when_associated(line, extension):
    with a.line_extension(line, extension, check=True):
        response = confd.extensions(extension['id']).put(context=INCALL_CONTEXT)
        response.assert_status(400)


@fixtures.line_sip()
@fixtures.extension()
def test_get_extension_relation(line, exten):
    with a.line_extension(line, exten):
        response = confd.lines(line['id']).get()
        assert_that(
            response.item['extensions'],
            contains(
                has_entries(
                    id=exten['id'], exten=exten['exten'], context=exten['context']
                )
            ),
        )


@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_get_line_relation(line, sip, extension):
    with a.line_endpoint_sip(line, sip):
        with a.line_extension(line, extension):
            line = confd.lines(line['id']).get().item
            response = confd.extensions(extension['id']).get()
            assert_that(
                response.item['lines'],
                contains(has_entries(id=line['id'], name=line['name'])),
            )


@fixtures.registrar()
def test_create_line_with_all_parameters_and_extension(registrar):
    exten = h.extension.find_available_exten(CONTEXT)
    response = confd.lines.post(
        context=CONTEXT,
        position=2,
        registrar=registrar['id'],
        provisioning_code='887865',
        extensions=[
            {
                'context': CONTEXT,
                'exten': exten,
            }
        ],
        endpoint_sip={
            'name': 'test',
        },
    )

    try:
        assert_that(
            response.item,
            has_entries(
                context=CONTEXT,
                position=2,
                device_slot=2,
                name='test',
                protocol='sip',
                device_id=none(),
                caller_id_name=none(),
                caller_id_num=none(),
                registrar=registrar['id'],
                provisioning_code="887865",
                provisioning_extension="887865",
                tenant_uuid=MAIN_TENANT,
                extensions=contains(
                    has_entries(
                        id=greater_than(0),
                        context=CONTEXT,
                        exten=exten,
                    )
                ),
            ),
        )

        assert_that(
            confd.lines(response.item['id']).get().item,
            has_entries(
                extensions=contains(
                    has_entries(
                        id=greater_than(0),
                        context=CONTEXT,
                        exten=exten,
                    )
                ),
            ),
        )

    finally:
        confd.lines(response.item['id']).delete().assert_deleted()


def test_create_line_extension_no_context():
    exten = h.extension.find_available_exten(CONTEXT)
    response = confd.lines.post(
        context=CONTEXT,
        extensions=[{'exten': exten}],
        endpoint_sip={'name': 'test'},
    )

    try:
        assert_that(
            response.item,
            has_entries(
                context=CONTEXT,
                extensions=contains(
                    has_entries(
                        context=CONTEXT,
                        exten=exten,
                    )
                ),
            ),
        )

        assert_that(
            confd.lines(response.item['id']).get().item,
            has_entries(
                extensions=contains(
                    has_entries(
                        context=CONTEXT,
                        exten=exten,
                    )
                ),
            ),
        )

    finally:
        confd.lines(response.item['id']).delete().assert_deleted()
