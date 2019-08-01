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
    with fixtures.group() as group, fixtures.schedule() as schedule:
        fake_group = confd.groups(FAKE_ID).schedules(schedule['id']).put
        fake_schedule = confd.groups(group['id']).schedules(FAKE_ID).put

        s.check_resource_not_found(fake_group, 'Group')
        s.check_resource_not_found(fake_schedule, 'Schedule')



def test_dissociate_errors():
    with fixtures.group() as group, fixtures.schedule() as schedule:
        fake_group = confd.groups(FAKE_ID).schedules(schedule['id']).delete
        fake_schedule = confd.groups(group['id']).schedules(FAKE_ID).delete

        s.check_resource_not_found(fake_group, 'Group')
        s.check_resource_not_found(fake_schedule, 'Schedule')



def test_associate():
    with fixtures.group() as group, fixtures.schedule() as schedule:
        response = confd.groups(group['id']).schedules(schedule['id']).put()
        response.assert_updated()



def test_associate_already_associated():
    with fixtures.group() as group, fixtures.schedule() as schedule:
        with a.group_schedule(group, schedule):
            response = confd.groups(group['id']).schedules(schedule['id']).put()
            response.assert_updated()


def test_associate_multiple_schedules_to_group():
    with fixtures.group() as group, fixtures.schedule() as schedule1, fixtures.schedule() as schedule2:
        with a.group_schedule(group, schedule1):
            response = confd.groups(group['id']).schedules(schedule2['id']).put()
            response.assert_match(400, e.resource_associated('Group', 'Schedule'))


def test_associate_multiple_groups_to_schedule():
    with fixtures.group() as group1, fixtures.group() as group2, fixtures.schedule() as schedule:
        with a.group_schedule(group1, schedule):
            response = confd.groups(group2['id']).schedules(schedule['id']).put()
            response.assert_updated()


def test_associate_multi_tenant():
    with fixtures.group(wazo_tenant=MAIN_TENANT) as main_group, fixtures.group(wazo_tenant=SUB_TENANT) as sub_group, fixtures.schedule(wazo_tenant=MAIN_TENANT) as main_schedule, fixtures.schedule(wazo_tenant=SUB_TENANT) as sub_schedule:
        response = confd.groups(main_group['id']).schedules(sub_schedule['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Group'))

        response = confd.groups(sub_group['id']).schedules(main_schedule['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Schedule'))

        response = confd.groups(main_group['id']).schedules(sub_schedule['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.group() as group, fixtures.schedule() as schedule:
        with a.group_schedule(group, schedule, check=False):
            response = confd.groups(group['id']).schedules(schedule['id']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.group() as group, fixtures.schedule() as schedule:
        response = confd.groups(group['id']).schedules(schedule['id']).delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.group(wazo_tenant=MAIN_TENANT) as main_group, fixtures.group(wazo_tenant=SUB_TENANT) as sub_group, fixtures.schedule(wazo_tenant=MAIN_TENANT) as main_schedule, fixtures.schedule(wazo_tenant=SUB_TENANT) as sub_schedule:
        response = confd.groups(main_group['id']).schedules(sub_schedule['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Group'))

        response = confd.groups(sub_group['id']).schedules(main_schedule['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Schedule'))



def test_get_group_relation():
    with fixtures.group() as group, fixtures.schedule() as schedule:
        with a.group_schedule(group, schedule):
            response = confd.groups(group['id']).get()
            assert_that(response.item, has_entries(
                schedules=contains(has_entries(id=schedule['id'],
                                               name=schedule['name']))
            ))


def test_get_schedule_relation():
    with fixtures.schedule() as schedule, fixtures.group() as group:
        with a.group_schedule(group, schedule):
            response = confd.schedules(schedule['id']).get()
            assert_that(response.item, has_entries(
                groups=contains(has_entries(id=group['id']))
            ))


def test_delete_group_when_group_and_schedule_associated():
    with fixtures.group() as group, fixtures.schedule() as schedule:
        with a.group_schedule(group, schedule, check=False):
            response = confd.groups(group['id']).delete()
            response.assert_deleted()


def test_delete_schedule_when_group_and_schedule_associated():
    with fixtures.group() as group, fixtures.schedule() as schedule:
        with a.group_schedule(group, schedule, check=False):
            response = confd.schedules(schedule['id']).delete()
            response.assert_deleted()
