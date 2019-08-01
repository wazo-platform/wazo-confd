# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    has_entries,
)

from ..helpers import (
    scenarios as s,
    errors as e,
    fixtures,
    associations as a,
)
from ..helpers.config import (
    EXTEN_OUTSIDE_RANGE,
    INCALL_CONTEXT,
    MAIN_TENANT,
    SUB_TENANT,
    gen_queue_exten,
)
from . import confd

FAKE_ID = 999999999


def test_associate_errors():
    with fixtures.extension(exten=gen_queue_exten()) as extension, fixtures.queue() as queue:
        fake_queue = confd.queues(FAKE_ID).extensions(extension['id']).put
        fake_extension = confd.queues(queue['id']).extensions(FAKE_ID).put

        s.check_resource_not_found(fake_queue, 'Queue')
        s.check_resource_not_found(fake_extension, 'Extension')



def test_dissociate_errors():
    with fixtures.extension(exten=gen_queue_exten()) as extension, fixtures.queue() as queue:
        fake_queue = confd.queues(FAKE_ID).extensions(extension['id']).delete
        fake_extension = confd.queues(queue['id']).extensions(FAKE_ID).delete

        s.check_resource_not_found(fake_queue, 'Queue')
        s.check_resource_not_found(fake_extension, 'Extension')



def test_associate():
    with fixtures.extension(exten=gen_queue_exten()) as extension, fixtures.queue() as queue:
        response = confd.queues(queue['id']).extensions(extension['id']).put()
        response.assert_updated()



def test_associate_already_associated():
    with fixtures.extension(exten=gen_queue_exten()) as extension, fixtures.queue() as queue:
        with a.queue_extension(queue, extension):
            response = confd.queues(queue['id']).extensions(extension['id']).put()
            response.assert_updated()


def test_associate_multiple_extensions_to_queue():
    with fixtures.extension(exten=gen_queue_exten()) as extension1, fixtures.extension(exten=gen_queue_exten()) as extension2, fixtures.queue() as queue:
        with a.queue_extension(queue, extension1):
            response = confd.queues(queue['id']).extensions(extension2['id']).put()
            response.assert_match(400, e.resource_associated('Queue', 'Extension'))


def test_associate_multiple_queues_to_extension():
    with fixtures.extension(exten=gen_queue_exten()) as extension, fixtures.queue() as queue1, fixtures.queue() as queue2:
        with a.queue_extension(queue1, extension):
            response = confd.queues(queue2['id']).extensions(extension['id']).put()
            response.assert_match(400, e.resource_associated('Queue', 'Extension'))


def test_associate_when_user_already_associated():
    with fixtures.extension() as extension, fixtures.queue() as queue, fixtures.user() as user, fixtures.line_sip() as line_sip:
        with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
            response = confd.queues(queue['id']).extensions(extension['id']).put()
            response.assert_match(400, e.resource_associated('user', 'Extension'))


def test_associate_when_not_internal_context():
    with fixtures.extension(exten=gen_queue_exten(), context=INCALL_CONTEXT) as extension, fixtures.queue() as queue:
        response = confd.queues(queue['id']).extensions(extension['id']).put()
        response.assert_status(400)



def test_associate_when_exten_outside_range():
    with fixtures.extension(exten=EXTEN_OUTSIDE_RANGE) as extension, fixtures.queue() as queue:
        response = confd.queues(queue['id']).extensions(extension['id']).put()
        response.assert_status(400)



def test_associate_when_exten_pattern():
    with fixtures.extension(exten='_5678') as extension, fixtures.queue() as queue:
        response = confd.queues(queue['id']).extensions(extension['id']).put()
        response.assert_updated()



def test_associate_multi_tenant():
    with fixtures.queue(wazo_tenant=MAIN_TENANT) as main_queue, fixtures.queue(wazo_tenant=SUB_TENANT) as sub_queue, fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal') as main_ctx, fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal') as sub_ctx, fixtures.extension(context='main-internal', exten=gen_queue_exten()) as main_exten, fixtures.extension(context='sub-internal', exten=gen_queue_exten()) as sub_exten:
        response = confd.queues(sub_queue['id']).extensions(main_exten['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        response = confd.queues(main_queue['id']).extensions(sub_exten['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Queue'))

        response = confd.queues(main_queue['id']).extensions(sub_exten['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.extension(exten=gen_queue_exten()) as extension, fixtures.queue() as queue:
        with a.queue_extension(queue, extension, check=False):
            response = confd.queues(queue['id']).extensions(extension['id']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.extension(exten=gen_queue_exten()) as extension, fixtures.queue() as queue:
        response = confd.queues(queue['id']).extensions(extension['id']).delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.queue(wazo_tenant=MAIN_TENANT) as main_queue, fixtures.queue(wazo_tenant=SUB_TENANT) as sub_queue, fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal') as main_ctx, fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal') as sub_ctx, fixtures.extension(context='main-internal', exten=gen_queue_exten()) as main_exten, fixtures.extension(context='sub-internal', exten=gen_queue_exten()) as sub_exten:
        response = confd.queues(sub_queue['id']).extensions(main_exten['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        response = confd.queues(main_queue['id']).extensions(sub_exten['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Queue'))



def test_get_queue_relation():
    with fixtures.extension(exten=gen_queue_exten()) as extension, fixtures.queue() as queue:
        with a.queue_extension(queue, extension):
            response = confd.queues(queue['id']).get()
            assert_that(response.item, has_entries(
                extensions=contains(has_entries(
                    id=extension['id'],
                    exten=extension['exten'],
                    context=extension['context']
                ))
            ))


def test_get_extension_relation():
    with fixtures.extension(exten=gen_queue_exten()) as extension, fixtures.queue() as queue:
        with a.queue_extension(queue, extension):
            response = confd.extensions(extension['id']).get()
            assert_that(response.item, has_entries(
                queue=has_entries(
                    id=queue['id'],
                    name=queue['name']
                )
            ))


def test_edit_context_to_incall_when_associated():
    with fixtures.extension(exten=gen_queue_exten()) as extension, fixtures.queue() as queue:
        with a.queue_extension(queue, extension):
            response = confd.extensions(extension['id']).put(context=INCALL_CONTEXT)
            response.assert_status(400)


def test_delete_queue_when_queue_and_extension_associated():
    with fixtures.extension(exten=gen_queue_exten()) as extension, fixtures.queue() as queue:
        with a.queue_extension(queue, extension, check=False):
            response = confd.queues(queue['id']).delete()
            response.assert_deleted()


def test_delete_extension_associated_to_queue():
    with fixtures.extension() as extension, fixtures.queue() as queue:
        # This operation should be possible in a better world
        with a.queue_extension(queue, extension):
            response = confd.extensions(extension['id']).delete()
            response.assert_match(400, e.resource_associated('Extension', 'queue'))



def test_bus_events():
    with fixtures.extension(exten=gen_queue_exten()) as extension, fixtures.queue() as queue:
        url = confd.queues(queue['id']).extensions(extension['id'])
        s.check_bus_event('config.queues.extensions.updated', url.put)
        s.check_bus_event('config.queues.extensions.deleted', url.delete)

