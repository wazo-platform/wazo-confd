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
    with fixtures.outcall() as outcall, fixtures.schedule() as schedule:
        fake_outcall = confd.outcalls(FAKE_ID).schedules(schedule['id']).put
        fake_schedule = confd.outcalls(outcall['id']).schedules(FAKE_ID).put

        s.check_resource_not_found(fake_outcall, 'Outcall')
        s.check_resource_not_found(fake_schedule, 'Schedule')



def test_dissociate_errors():
    with fixtures.outcall() as outcall, fixtures.schedule() as schedule:
        fake_outcall = confd.outcalls(FAKE_ID).schedules(schedule['id']).delete
        fake_schedule = confd.outcalls(outcall['id']).schedules(FAKE_ID).delete

        s.check_resource_not_found(fake_outcall, 'Outcall')
        s.check_resource_not_found(fake_schedule, 'Schedule')



def test_associate():
    with fixtures.outcall() as outcall, fixtures.schedule() as schedule:
        response = confd.outcalls(outcall['id']).schedules(schedule['id']).put()
        response.assert_updated()



def test_associate_already_associated():
    with fixtures.outcall() as outcall, fixtures.schedule() as schedule:
        with a.outcall_schedule(outcall, schedule):
            response = confd.outcalls(outcall['id']).schedules(schedule['id']).put()
            response.assert_updated()


def test_associate_multiple_schedules_to_outcall():
    with fixtures.outcall() as outcall, fixtures.schedule() as schedule1, fixtures.schedule() as schedule2:
        with a.outcall_schedule(outcall, schedule1):
            response = confd.outcalls(outcall['id']).schedules(schedule2['id']).put()
            response.assert_match(400, e.resource_associated('Outcall', 'Schedule'))


def test_associate_multiple_outcalls_to_schedule():
    with fixtures.outcall() as outcall1, fixtures.outcall() as outcall2, fixtures.schedule() as schedule:
        with a.outcall_schedule(outcall1, schedule):
            response = confd.outcalls(outcall2['id']).schedules(schedule['id']).put()
            response.assert_updated()


def test_associate_multi_tenant():
    with fixtures.outcall(wazo_tenant=MAIN_TENANT) as main_outcall, fixtures.outcall(wazo_tenant=SUB_TENANT) as sub_outcall, fixtures.schedule(wazo_tenant=MAIN_TENANT) as main_schedule, fixtures.schedule(wazo_tenant=SUB_TENANT) as sub_schedule:
        response = confd.outcalls(main_outcall['id']).schedules(sub_schedule['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Outcall'))

        response = confd.outcalls(sub_outcall['id']).schedules(main_schedule['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Schedule'))

        response = confd.outcalls(main_outcall['id']).schedules(sub_schedule['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.outcall() as outcall, fixtures.schedule() as schedule:
        with a.outcall_schedule(outcall, schedule, check=False):
            response = confd.outcalls(outcall['id']).schedules(schedule['id']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.outcall() as outcall, fixtures.schedule() as schedule:
        response = confd.outcalls(outcall['id']).schedules(schedule['id']).delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.outcall(wazo_tenant=MAIN_TENANT) as main_outcall, fixtures.outcall(wazo_tenant=SUB_TENANT) as sub_outcall, fixtures.schedule(wazo_tenant=MAIN_TENANT) as main_schedule, fixtures.schedule(wazo_tenant=SUB_TENANT) as sub_schedule:
        response = confd.outcalls(main_outcall['id']).schedules(sub_schedule['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Outcall'))

        response = confd.outcalls(sub_outcall['id']).schedules(main_schedule['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Schedule'))



def test_get_outcall_relation():
    with fixtures.outcall() as outcall, fixtures.schedule() as schedule:
        with a.outcall_schedule(outcall, schedule):
            response = confd.outcalls(outcall['id']).get()
            assert_that(response.item, has_entries(
                schedules=contains(has_entries(id=schedule['id'], name=schedule['name']))
            ))


def test_get_schedule_relation():
    with fixtures.schedule() as schedule, fixtures.outcall() as outcall:
        with a.outcall_schedule(outcall, schedule):
            response = confd.schedules(schedule['id']).get()
            assert_that(response.item, has_entries(
                outcalls=contains(has_entries(id=outcall['id']))
            ))


def test_delete_outcall_when_outcall_and_schedule_associated():
    with fixtures.outcall() as outcall, fixtures.schedule() as schedule:
        with a.outcall_schedule(outcall, schedule, check=False):
            response = confd.outcalls(outcall['id']).delete()
            response.assert_deleted()


def test_delete_schedule_when_outcall_and_schedule_associated():
    with fixtures.outcall() as outcall, fixtures.schedule() as schedule:
        with a.outcall_schedule(outcall, schedule, check=False):
            response = confd.schedules(schedule['id']).delete()
            response.assert_deleted()
