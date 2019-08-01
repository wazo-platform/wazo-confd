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


def test_associate_errors():
    with fixtures.queue() as queue, fixtures.schedule() as schedule:
        fake_queue = confd.queues(FAKE_ID).schedules(schedule['id']).put
        fake_schedule = confd.queues(queue['id']).schedules(FAKE_ID).put

        s.check_resource_not_found(fake_queue, 'Queue')
        s.check_resource_not_found(fake_schedule, 'Schedule')



def test_dissociate_errors():
    with fixtures.queue() as queue, fixtures.schedule() as schedule:
        fake_queue = confd.queues(FAKE_ID).schedules(schedule['id']).delete
        fake_schedule = confd.queues(queue['id']).schedules(FAKE_ID).delete

        s.check_resource_not_found(fake_queue, 'Queue')
        s.check_resource_not_found(fake_schedule, 'Schedule')



def test_associate():
    with fixtures.queue() as queue, fixtures.schedule() as schedule:
        response = confd.queues(queue['id']).schedules(schedule['id']).put()
        response.assert_updated()



def test_associate_already_associated():
    with fixtures.queue() as queue, fixtures.schedule() as schedule:
        with a.queue_schedule(queue, schedule):
            response = confd.queues(queue['id']).schedules(schedule['id']).put()
            response.assert_updated()


def test_associate_multiple_schedules_to_queue():
    with fixtures.queue() as queue, fixtures.schedule() as schedule1, fixtures.schedule() as schedule2:
        with a.queue_schedule(queue, schedule1):
            response = confd.queues(queue['id']).schedules(schedule2['id']).put()
            response.assert_match(400, e.resource_associated('Queue', 'Schedule'))


def test_associate_multiple_queues_to_schedule():
    with fixtures.queue() as queue1, fixtures.queue() as queue2, fixtures.schedule() as schedule:
        with a.queue_schedule(queue1, schedule):
            response = confd.queues(queue2['id']).schedules(schedule['id']).put()
            response.assert_updated()


def test_associate_multi_tenant():
    with fixtures.queue(wazo_tenant=MAIN_TENANT) as main_queue, fixtures.queue(wazo_tenant=SUB_TENANT) as sub_queue, fixtures.schedule(wazo_tenant=MAIN_TENANT) as main_schedule, fixtures.schedule(wazo_tenant=SUB_TENANT) as sub_schedule:
        response = confd.queues(main_queue['id']).schedules(sub_schedule['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Queue'))

        response = confd.queues(sub_queue['id']).schedules(main_schedule['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Schedule'))

        response = confd.queues(main_queue['id']).schedules(sub_schedule['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.queue() as queue, fixtures.schedule() as schedule:
        with a.queue_schedule(queue, schedule, check=False):
            response = confd.queues(queue['id']).schedules(schedule['id']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.queue() as queue, fixtures.schedule() as schedule:
        response = confd.queues(queue['id']).schedules(schedule['id']).delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.queue(wazo_tenant=MAIN_TENANT) as main_queue, fixtures.queue(wazo_tenant=SUB_TENANT) as sub_queue, fixtures.schedule(wazo_tenant=MAIN_TENANT) as main_schedule, fixtures.schedule(wazo_tenant=SUB_TENANT) as sub_schedule:
        response = confd.queues(main_queue['id']).schedules(sub_schedule['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Queue'))

        response = confd.queues(sub_queue['id']).schedules(main_schedule['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Schedule'))



def test_get_queue_relation():
    with fixtures.queue() as queue, fixtures.schedule() as schedule:
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


def test_get_schedule_relation():
    with fixtures.schedule() as schedule, fixtures.queue() as queue:
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


def test_delete_queue_when_queue_and_schedule_associated():
    with fixtures.queue() as queue, fixtures.schedule() as schedule:
        with a.queue_schedule(queue, schedule, check=False):
            response = confd.queues(queue['id']).delete()
            response.assert_deleted()


def test_delete_schedule_when_queue_and_schedule_associated():
    with fixtures.queue() as queue, fixtures.schedule() as schedule:
        with a.queue_schedule(queue, schedule, check=False):
            response = confd.schedules(schedule['id']).delete()
            response.assert_deleted()
