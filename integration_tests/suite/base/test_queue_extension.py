# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
    gen_queue_exten,
)
from . import confd

FAKE_ID = 999999999


@fixtures.queue()
@fixtures.extension(exten=gen_queue_exten())
def test_associate_errors(queue, extension):
    fake_queue = confd.queues(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.queues(queue['id']).extensions(FAKE_ID).put

    yield s.check_resource_not_found, fake_queue, 'Queue'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.queue()
@fixtures.extension(exten=gen_queue_exten())
def test_dissociate_errors(queue, extension):
    fake_queue = confd.queues(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.queues(queue['id']).extensions(FAKE_ID).delete

    yield s.check_resource_not_found, fake_queue, 'Queue'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.queue()
@fixtures.extension(exten=gen_queue_exten())
def test_associate(queue, extension):
    response = confd.queues(queue['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.queue()
@fixtures.extension(exten=gen_queue_exten())
def test_associate_already_associated(queue, extension):
    with a.queue_extension(queue, extension):
        response = confd.queues(queue['id']).extensions(extension['id']).put()
        response.assert_updated()


@fixtures.queue()
@fixtures.extension(exten=gen_queue_exten())
@fixtures.extension(exten=gen_queue_exten())
def test_associate_multiple_extensions_to_queue(queue, extension1, extension2):
    with a.queue_extension(queue, extension1):
        response = confd.queues(queue['id']).extensions(extension2['id']).put()
        response.assert_match(400, e.resource_associated('Queue', 'Extension'))


@fixtures.queue()
@fixtures.queue()
@fixtures.extension(exten=gen_queue_exten())
def test_associate_multiple_queues_to_extension(queue1, queue2, extension):
    with a.queue_extension(queue1, extension):
        response = confd.queues(queue2['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('Queue', 'Extension'))


@fixtures.queue()
@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_associate_when_user_already_associated(queue, user, line_sip, extension):
    with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
        response = confd.queues(queue['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('user', 'Extension'))


@fixtures.queue()
@fixtures.extension(exten=gen_queue_exten(), context=INCALL_CONTEXT)
def test_associate_when_not_internal_context(queue, extension):
    response = confd.queues(queue['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.queue()
@fixtures.extension(exten=EXTEN_OUTSIDE_RANGE)
def test_associate_when_exten_outside_range(queue, extension):
    response = confd.queues(queue['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.queue()
@fixtures.extension(exten='_5678')
def test_associate_when_exten_pattern(queue, extension):
    response = confd.queues(queue['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.queue()
@fixtures.extension(exten=gen_queue_exten())
def test_dissociate(queue, extension):
    with a.queue_extension(queue, extension, check=False):
        response = confd.queues(queue['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.queue()
@fixtures.extension(exten=gen_queue_exten())
def test_dissociate_not_associated(queue, extension):
    response = confd.queues(queue['id']).extensions(extension['id']).delete()
    response.assert_deleted()


@fixtures.queue()
@fixtures.extension(exten=gen_queue_exten())
def test_get_queue_relation(queue, extension):
    with a.queue_extension(queue, extension):
        response = confd.queues(queue['id']).get()
        assert_that(response.item, has_entries(
            extensions=contains(has_entries(
                id=extension['id'],
                exten=extension['exten'],
                context=extension['context']
            ))
        ))


@fixtures.extension(exten=gen_queue_exten())
@fixtures.queue()
def test_get_extension_relation(extension, queue):
    with a.queue_extension(queue, extension):
        response = confd.extensions(extension['id']).get()
        assert_that(response.item, has_entries(
            queue=has_entries(
                id=queue['id'],
                name=queue['name']
            )
        ))


@fixtures.queue()
@fixtures.extension(exten=gen_queue_exten())
def test_edit_context_to_incall_when_associated(queue, extension):
    with a.queue_extension(queue, extension):
        response = confd.extensions(extension['id']).put(context=INCALL_CONTEXT)
        response.assert_status(400)


@fixtures.queue()
@fixtures.extension(exten=gen_queue_exten())
def test_delete_queue_when_queue_and_extension_associated(queue, extension):
    with a.queue_extension(queue, extension, check=False):
        response = confd.queues(queue['id']).delete()
        response.assert_deleted()


@fixtures.queue()
@fixtures.extension()
def test_delete_extension_associated_to_queue(queue, extension):
    # This operation should be possible in a better world
    with a.queue_extension(queue, extension):
        response = confd.extensions(extension['id']).delete()
        response.assert_match(400, e.resource_associated('Extension', 'queue'))


@fixtures.queue()
@fixtures.extension(exten=gen_queue_exten())
def test_bus_events(queue, extension):
    url = confd.queues(queue['id']).extensions(extension['id'])
    yield s.check_bus_event, 'config.queues.extensions.updated', url.put
    yield s.check_bus_event, 'config.queues.extensions.deleted', url.delete
