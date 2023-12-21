# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
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
    gen_queue_exten,
)
from . import confd

FAKE_ID = 999999999


@fixtures.extension(exten=gen_queue_exten())
@fixtures.queue()
def test_associate_errors(extension, queue):
    fake_queue = confd.queues(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.queues(queue['id']).extensions(FAKE_ID).put

    yield s.check_resource_not_found, fake_queue, 'Queue'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.extension(exten=gen_queue_exten())
@fixtures.queue()
def test_dissociate_errors(extension, queue):
    fake_queue = confd.queues(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.queues(queue['id']).extensions(FAKE_ID).delete

    yield s.check_resource_not_found, fake_queue, 'Queue'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.extension(exten=gen_queue_exten())
@fixtures.queue()
def test_associate(extension, queue):
    response = confd.queues(queue['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.extension(exten=gen_queue_exten())
@fixtures.queue()
def test_associate_already_associated(extension, queue):
    with a.queue_extension(queue, extension):
        response = confd.queues(queue['id']).extensions(extension['id']).put()
        response.assert_updated()


@fixtures.extension(exten=gen_queue_exten())
@fixtures.extension(exten=gen_queue_exten())
@fixtures.queue()
def test_associate_multiple_extensions_to_queue(extension1, extension2, queue):
    with a.queue_extension(queue, extension1):
        response = confd.queues(queue['id']).extensions(extension2['id']).put()
        response.assert_match(400, e.resource_associated('Queue', 'Extension'))


@fixtures.extension(exten=gen_queue_exten())
@fixtures.queue()
@fixtures.queue()
def test_associate_multiple_queues_to_extension(extension, queue1, queue2):
    with a.queue_extension(queue1, extension):
        response = confd.queues(queue2['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('Queue', 'Extension'))


@fixtures.extension()
@fixtures.queue()
@fixtures.user()
@fixtures.line_sip()
def test_associate_when_user_already_associated(extension, queue, user, line_sip):
    with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
        response = confd.queues(queue['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('user', 'Extension'))


@fixtures.extension(exten=gen_queue_exten(), context=INCALL_CONTEXT)
@fixtures.queue()
def test_associate_when_not_internal_context(extension, queue):
    response = confd.queues(queue['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.extension(exten=EXTEN_OUTSIDE_RANGE)
@fixtures.queue()
def test_associate_when_exten_outside_range(extension, queue):
    response = confd.queues(queue['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.extension(exten='_5678')
@fixtures.queue()
def test_associate_when_exten_pattern(extension, queue):
    response = confd.queues(queue['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.queue(wazo_tenant=MAIN_TENANT)
@fixtures.queue(wazo_tenant=SUB_TENANT)
@fixtures.context(wazo_tenant=MAIN_TENANT, label='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, label='sub-internal')
def test_associate_multi_tenant(main_queue, sub_queue, main_ctx, sub_ctx):
    with fixtures.extension(
        context=main_ctx['name'], exten=gen_queue_exten()
    ) as main_exten:
        with fixtures.extension(
            context=sub_ctx['name'], exten=gen_queue_exten()
        ) as sub_exten:
            response = (
                confd.queues(sub_queue['id'])
                .extensions(main_exten['id'])
                .put(wazo_tenant=SUB_TENANT)
            )
            response.assert_match(404, e.not_found('Extension'))

            response = (
                confd.queues(main_queue['id'])
                .extensions(sub_exten['id'])
                .put(wazo_tenant=SUB_TENANT)
            )
            response.assert_match(404, e.not_found('Queue'))

            response = (
                confd.queues(main_queue['id'])
                .extensions(sub_exten['id'])
                .put(wazo_tenant=MAIN_TENANT)
            )
            response.assert_match(400, e.different_tenant())


@fixtures.extension(exten=gen_queue_exten())
@fixtures.queue()
def test_dissociate(extension, queue):
    with a.queue_extension(queue, extension, check=False):
        response = confd.queues(queue['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.extension(exten=gen_queue_exten())
@fixtures.queue()
def test_dissociate_not_associated(extension, queue):
    response = confd.queues(queue['id']).extensions(extension['id']).delete()
    response.assert_deleted()


@fixtures.queue(wazo_tenant=MAIN_TENANT)
@fixtures.queue(wazo_tenant=SUB_TENANT)
@fixtures.context(wazo_tenant=MAIN_TENANT, label='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, label='sub-internal')
def test_dissociate_multi_tenant(main_queue, sub_queue, main_ctx, sub_ctx):
    with fixtures.extension(
        context=main_ctx['name'], exten=gen_queue_exten()
    ) as main_exten:
        with fixtures.extension(
            context=sub_ctx['name'], exten=gen_queue_exten()
        ) as sub_exten:
            response = (
                confd.queues(sub_queue['id'])
                .extensions(main_exten['id'])
                .delete(wazo_tenant=SUB_TENANT)
            )
            response.assert_match(404, e.not_found('Extension'))

            response = (
                confd.queues(main_queue['id'])
                .extensions(sub_exten['id'])
                .delete(wazo_tenant=SUB_TENANT)
            )
            response.assert_match(404, e.not_found('Queue'))


@fixtures.extension(exten=gen_queue_exten())
@fixtures.queue()
def test_get_queue_relation(extension, queue):
    with a.queue_extension(queue, extension):
        response = confd.queues(queue['id']).get()
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


@fixtures.extension(exten=gen_queue_exten())
@fixtures.queue()
def test_get_extension_relation(extension, queue):
    with a.queue_extension(queue, extension):
        response = confd.extensions(extension['id']).get()
        assert_that(
            response.item,
            has_entries(queue=has_entries(id=queue['id'], name=queue['name'])),
        )


@fixtures.extension(exten=gen_queue_exten())
@fixtures.queue()
def test_edit_context_to_incall_when_associated(extension, queue):
    with a.queue_extension(queue, extension):
        response = confd.extensions(extension['id']).put(context=INCALL_CONTEXT)
        response.assert_status(400)


@fixtures.extension(exten=gen_queue_exten())
@fixtures.queue()
def test_delete_queue_when_queue_and_extension_associated(extension, queue):
    with a.queue_extension(queue, extension, check=False):
        response = confd.queues(queue['id']).delete()
        response.assert_deleted()


@fixtures.extension()
@fixtures.queue()
def test_delete_extension_associated_to_queue(extension, queue):
    # This operation should be possible in a better world
    with a.queue_extension(queue, extension):
        response = confd.extensions(extension['id']).delete()
        response.assert_match(400, e.resource_associated('Extension', 'queue'))


@fixtures.extension(exten=gen_queue_exten())
@fixtures.queue()
def test_bus_events(extension, queue):
    url = confd.queues(queue['id']).extensions(extension['id'])
    headers = {'tenant_uuid': queue['tenant_uuid']}

    yield s.check_event, 'queue_extension_associated', headers, url.put
    yield s.check_event, 'queue_extension_dissociated', headers, url.delete
