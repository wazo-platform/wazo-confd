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


@fixtures.group()
@fixtures.schedule()
def test_associate_errors(group, schedule):
    fake_group = confd.groups(FAKE_ID).schedules(schedule['id']).put
    fake_schedule = confd.groups(group['id']).schedules(FAKE_ID).put

    s.check_resource_not_found(fake_group, 'Group')
    s.check_resource_not_found(fake_schedule, 'Schedule')


@fixtures.group()
@fixtures.schedule()
def test_dissociate_errors(group, schedule):
    fake_group = confd.groups(FAKE_ID).schedules(schedule['id']).delete
    fake_schedule = confd.groups(group['id']).schedules(FAKE_ID).delete

    s.check_resource_not_found(fake_group, 'Group')
    s.check_resource_not_found(fake_schedule, 'Schedule')


@fixtures.group()
@fixtures.schedule()
def test_associate(group, schedule):
    response = confd.groups(group['id']).schedules(schedule['id']).put()
    response.assert_updated()


@fixtures.group()
@fixtures.schedule()
def test_associate_already_associated(group, schedule):
    with a.group_schedule(group, schedule):
        response = confd.groups(group['id']).schedules(schedule['id']).put()
        response.assert_updated()


@fixtures.group()
@fixtures.schedule()
@fixtures.schedule()
def test_associate_multiple_schedules_to_group(group, schedule1, schedule2):
    with a.group_schedule(group, schedule1):
        response = confd.groups(group['id']).schedules(schedule2['id']).put()
        response.assert_match(400, e.resource_associated('Group', 'Schedule'))


@fixtures.group()
@fixtures.group()
@fixtures.schedule()
def test_associate_multiple_groups_to_schedule(group1, group2, schedule):
    with a.group_schedule(group1, schedule):
        response = confd.groups(group2['id']).schedules(schedule['id']).put()
        response.assert_updated()


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
@fixtures.schedule(wazo_tenant=MAIN_TENANT)
@fixtures.schedule(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_group, sub_group, main_schedule, sub_schedule):
    response = confd.groups(main_group['id']).schedules(sub_schedule['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Group'))

    response = confd.groups(sub_group['id']).schedules(main_schedule['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Schedule'))

    response = confd.groups(main_group['id']).schedules(sub_schedule['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())


@fixtures.group()
@fixtures.schedule()
def test_dissociate(group, schedule):
    with a.group_schedule(group, schedule, check=False):
        response = confd.groups(group['id']).schedules(schedule['id']).delete()
        response.assert_deleted()


@fixtures.group()
@fixtures.schedule()
def test_dissociate_not_associated(group, schedule):
    response = confd.groups(group['id']).schedules(schedule['id']).delete()
    response.assert_deleted()


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
@fixtures.schedule(wazo_tenant=MAIN_TENANT)
@fixtures.schedule(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(main_group, sub_group, main_schedule, sub_schedule):
    response = confd.groups(main_group['id']).schedules(sub_schedule['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Group'))

    response = confd.groups(sub_group['id']).schedules(main_schedule['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Schedule'))


@fixtures.group()
@fixtures.schedule()
def test_get_group_relation(group, schedule):
    with a.group_schedule(group, schedule):
        response = confd.groups(group['id']).get()
        assert_that(response.item, has_entries(
            schedules=contains(has_entries(id=schedule['id'],
                                           name=schedule['name']))
        ))


@fixtures.schedule()
@fixtures.group()
def test_get_schedule_relation(schedule, group):
    with a.group_schedule(group, schedule):
        response = confd.schedules(schedule['id']).get()
        assert_that(response.item, has_entries(
            groups=contains(has_entries(id=group['id']))
        ))


@fixtures.group()
@fixtures.schedule()
def test_delete_group_when_group_and_schedule_associated(group, schedule):
    with a.group_schedule(group, schedule, check=False):
        response = confd.groups(group['id']).delete()
        response.assert_deleted()


@fixtures.group()
@fixtures.schedule()
def test_delete_schedule_when_group_and_schedule_associated(group, schedule):
    with a.group_schedule(group, schedule, check=False):
        response = confd.schedules(schedule['id']).delete()
        response.assert_deleted()
