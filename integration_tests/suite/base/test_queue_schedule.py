# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
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
    MAIN_TENANT,
    SUB_TENANT,
)

FAKE_ID = 999999999


@fixtures.queue()
@fixtures.schedule()
def test_associate_errors(queue, schedule):
    fake_queue = confd.queues(FAKE_ID).schedules(schedule['id']).put
    fake_schedule = confd.queues(queue['id']).schedules(FAKE_ID).put

    yield s.check_resource_not_found, fake_queue, 'Queue'
    yield s.check_resource_not_found, fake_schedule, 'Schedule'


@fixtures.queue()
@fixtures.schedule()
def test_dissociate_errors(queue, schedule):
    fake_queue = confd.queues(FAKE_ID).schedules(schedule['id']).delete
    fake_schedule = confd.queues(queue['id']).schedules(FAKE_ID).delete

    yield s.check_resource_not_found, fake_queue, 'Queue'
    yield s.check_resource_not_found, fake_schedule, 'Schedule'


@fixtures.queue()
@fixtures.schedule()
def test_associate(queue, schedule):
    response = confd.queues(queue['id']).schedules(schedule['id']).put()
    response.assert_updated()


@fixtures.queue()
@fixtures.schedule()
def test_associate_already_associated(queue, schedule):
    with a.queue_schedule(queue, schedule):
        response = confd.queues(queue['id']).schedules(schedule['id']).put()
        response.assert_updated()


@fixtures.queue()
@fixtures.schedule()
@fixtures.schedule()
def test_associate_multiple_schedules_to_queue(queue, schedule1, schedule2):
    with a.queue_schedule(queue, schedule1):
        response = confd.queues(queue['id']).schedules(schedule2['id']).put()
        response.assert_match(400, e.resource_associated('Queue', 'Schedule'))


@fixtures.queue()
@fixtures.queue()
@fixtures.schedule()
def test_associate_multiple_queues_to_schedule(queue1, queue2, schedule):
    with a.queue_schedule(queue1, schedule):
        response = confd.queues(queue2['id']).schedules(schedule['id']).put()
        response.assert_updated()


@fixtures.queue(wazo_tenant=MAIN_TENANT)
@fixtures.queue(wazo_tenant=SUB_TENANT)
@fixtures.schedule(wazo_tenant=MAIN_TENANT)
@fixtures.schedule(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_queue, sub_queue, main_schedule, sub_schedule):
    response = confd.queues(main_queue['id']).schedules(sub_schedule['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Queue'))

    response = confd.queues(sub_queue['id']).schedules(main_schedule['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Schedule'))

    response = confd.queues(main_queue['id']).schedules(sub_schedule['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())


@fixtures.queue()
@fixtures.schedule()
def test_dissociate(queue, schedule):
    with a.queue_schedule(queue, schedule, check=False):
        response = confd.queues(queue['id']).schedules(schedule['id']).delete()
        response.assert_deleted()


@fixtures.queue()
@fixtures.schedule()
def test_dissociate_not_associated(queue, schedule):
    response = confd.queues(queue['id']).schedules(schedule['id']).delete()
    response.assert_deleted()


@fixtures.queue(wazo_tenant=MAIN_TENANT)
@fixtures.queue(wazo_tenant=SUB_TENANT)
@fixtures.schedule(wazo_tenant=MAIN_TENANT)
@fixtures.schedule(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(main_queue, sub_queue, main_schedule, sub_schedule):
    response = confd.queues(main_queue['id']).schedules(sub_schedule['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Queue'))

    response = confd.queues(sub_queue['id']).schedules(main_schedule['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Schedule'))


@fixtures.queue()
@fixtures.schedule()
def test_get_queue_relation(queue, schedule):
    with a.queue_schedule(queue, schedule):
        response = confd.queues(queue['id']).get()
        assert_that(response.item, has_entries(
            schedules=contains(
                has_entries(
                    id=schedule['id'],
                    name=schedule['name'],
                )
            )
        ))


@fixtures.schedule()
@fixtures.queue()
def test_get_schedule_relation(schedule, queue):
    with a.queue_schedule(queue, schedule):
        response = confd.schedules(schedule['id']).get()
        assert_that(response.item, has_entries(
            queues=contains(
                has_entries(
                    id=queue['id'],
                    name=queue['name'],
                    label=queue['label'],
                )
            )
        ))


@fixtures.queue()
@fixtures.schedule()
def test_delete_queue_when_queue_and_schedule_associated(queue, schedule):
    with a.queue_schedule(queue, schedule, check=False):
        response = confd.queues(queue['id']).delete()
        response.assert_deleted()


@fixtures.queue()
@fixtures.schedule()
def test_delete_schedule_when_queue_and_schedule_associated(queue, schedule):
    with a.queue_schedule(queue, schedule, check=False):
        response = confd.schedules(schedule['id']).delete()
        response.assert_deleted()
