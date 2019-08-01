# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
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
    with fixtures.incall() as incall, fixtures.schedule() as schedule:
        fake_incall = confd.incalls(FAKE_ID).schedules(schedule['id']).put
        fake_schedule = confd.incalls(incall['id']).schedules(FAKE_ID).put

        s.check_resource_not_found(fake_incall, 'Incall')
        s.check_resource_not_found(fake_schedule, 'Schedule')



def test_dissociate_errors():
    with fixtures.incall() as incall, fixtures.schedule() as schedule:
        fake_incall = confd.incalls(FAKE_ID).schedules(schedule['id']).delete
        fake_schedule = confd.incalls(incall['id']).schedules(FAKE_ID).delete

        s.check_resource_not_found(fake_incall, 'Incall')
        s.check_resource_not_found(fake_schedule, 'Schedule')



def test_associate():
    with fixtures.incall() as incall, fixtures.schedule() as schedule:
        response = confd.incalls(incall['id']).schedules(schedule['id']).put()
        response.assert_updated()



def test_associate_already_associated():
    with fixtures.incall() as incall, fixtures.schedule() as schedule:
        with a.incall_schedule(incall, schedule):
            response = confd.incalls(incall['id']).schedules(schedule['id']).put()
            response.assert_updated()


def test_associate_multiple_schedules_to_incall():
    with fixtures.incall() as incall, fixtures.schedule() as schedule1, fixtures.schedule() as schedule2:
        with a.incall_schedule(incall, schedule1):
            response = confd.incalls(incall['id']).schedules(schedule2['id']).put()
            response.assert_match(400, e.resource_associated('Incall', 'Schedule'))


def test_associate_multiple_incalls_to_schedule():
    with fixtures.incall() as incall1, fixtures.incall() as incall2, fixtures.schedule() as schedule:
        with a.incall_schedule(incall1, schedule):
            response = confd.incalls(incall2['id']).schedules(schedule['id']).put()
            response.assert_updated()


def test_associate_multi_tenant():
    with fixtures.incall(wazo_tenant=MAIN_TENANT) as main_incall, fixtures.incall(wazo_tenant=SUB_TENANT) as sub_incall, fixtures.schedule(wazo_tenant=MAIN_TENANT) as main_schedule, fixtures.schedule(wazo_tenant=SUB_TENANT) as sub_schedule:
        response = confd.incalls(main_incall['id']).schedules(sub_schedule['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Incall'))

        response = confd.incalls(sub_incall['id']).schedules(main_schedule['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Schedule'))

        response = confd.incalls(main_incall['id']).schedules(sub_schedule['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.incall() as incall, fixtures.schedule() as schedule:
        with a.incall_schedule(incall, schedule, check=False):
            response = confd.incalls(incall['id']).schedules(schedule['id']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.incall() as incall, fixtures.schedule() as schedule:
        response = confd.incalls(incall['id']).schedules(schedule['id']).delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.incall(wazo_tenant=MAIN_TENANT) as main_incall, fixtures.incall(wazo_tenant=SUB_TENANT) as sub_incall, fixtures.schedule(wazo_tenant=MAIN_TENANT) as main_schedule, fixtures.schedule(wazo_tenant=SUB_TENANT) as sub_schedule:
        response = confd.incalls(main_incall['id']).schedules(sub_schedule['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Incall'))

        response = confd.incalls(sub_incall['id']).schedules(main_schedule['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Schedule'))



def test_get_incall_relation():
    with fixtures.incall() as incall, fixtures.schedule() as schedule:
        with a.incall_schedule(incall, schedule):
            response = confd.incalls(incall['id']).get()
            assert_that(response.item, has_entries(
                schedules=contains(has_entries(id=schedule['id'], name=schedule['name']))
            ))


def test_get_schedule_relation():
    with fixtures.schedule() as schedule, fixtures.incall() as incall:
        with a.incall_schedule(incall, schedule):
            response = confd.schedules(schedule['id']).get()
            assert_that(response.item, has_entries(
                incalls=contains(has_entries(id=incall['id']))
            ))


def test_delete_incall_when_incall_and_schedule_associated():
    with fixtures.incall() as incall, fixtures.schedule() as schedule:
        with a.incall_schedule(incall, schedule, check=False):
            response = confd.incalls(incall['id']).delete()
            response.assert_deleted()


def test_delete_schedule_when_incall_and_schedule_associated():
    with fixtures.incall() as incall, fixtures.schedule() as schedule:
        with a.incall_schedule(incall, schedule, check=False):
            response = confd.schedules(schedule['id']).delete()
            response.assert_deleted()
