# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      contains,
                      has_entries)
from ..helpers import scenarios as s
from . import confd
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import associations as a


FAKE_ID = 999999999


@fixtures.incall()
@fixtures.schedule()
def test_associate_errors(incall, schedule):
    fake_incall = confd.incalls(FAKE_ID).schedules(schedule['id']).put
    fake_schedule = confd.incalls(incall['id']).schedules(FAKE_ID).put

    yield s.check_resource_not_found, fake_incall, 'Incall'
    yield s.check_resource_not_found, fake_schedule, 'Schedule'


@fixtures.incall()
@fixtures.schedule()
def test_dissociate_errors(incall, schedule):
    fake_incall_schedule = confd.incalls(incall['id']).schedules(schedule['id']).delete
    fake_incall = confd.incalls(FAKE_ID).schedules(schedule['id']).delete
    fake_schedule = confd.incalls(incall['id']).schedules(FAKE_ID).delete

    yield s.check_resource_not_found, fake_incall, 'Incall'
    yield s.check_resource_not_found, fake_schedule, 'Schedule'
    yield s.check_resource_not_found, fake_incall_schedule, 'IncallSchedule'


@fixtures.incall()
@fixtures.schedule()
def test_associate(incall, schedule):
    response = confd.incalls(incall['id']).schedules(schedule['id']).put()
    response.assert_updated()


@fixtures.incall()
@fixtures.schedule()
def test_associate_already_associated(incall, schedule):
    with a.incall_schedule(incall, schedule):
        response = confd.incalls(incall['id']).schedules(schedule['id']).put()
        response.assert_match(400, e.resource_associated('Incall', 'Schedule'))


@fixtures.incall()
@fixtures.schedule()
@fixtures.schedule()
def test_associate_multiple_schedules_to_incall(incall, schedule1, schedule2):
    with a.incall_schedule(incall, schedule1):
        response = confd.incalls(incall['id']).schedules(schedule2['id']).put()
        response.assert_match(400, e.resource_associated('Incall', 'Schedule'))


@fixtures.incall()
@fixtures.incall()
@fixtures.schedule()
def test_associate_multiple_incalls_to_schedule(incall1, incall2, schedule):
    with a.incall_schedule(incall1, schedule):
        response = confd.incalls(incall2['id']).schedules(schedule['id']).put()
        response.assert_updated()


@fixtures.incall()
@fixtures.schedule()
def test_dissociate(incall, schedule):
    with a.incall_schedule(incall, schedule, check=False):
        response = confd.incalls(incall['id']).schedules(schedule['id']).delete()
        response.assert_deleted()


@fixtures.incall()
@fixtures.schedule()
def test_get_incall_relation(incall, schedule):
    with a.incall_schedule(incall, schedule):
        response = confd.incalls(incall['id']).get()
        assert_that(response.item, has_entries(
            schedules=contains(has_entries(id=schedule['id'],
                                           name=schedule['name']))
        ))


@fixtures.schedule()
@fixtures.incall()
def test_get_schedule_relation(schedule, incall):
    with a.incall_schedule(incall, schedule):
        response = confd.schedules(schedule['id']).get()
        assert_that(response.item, has_entries(
            incalls=contains(has_entries(id=incall['id']))
        ))


@fixtures.incall()
@fixtures.schedule()
def test_delete_incall_when_incall_and_schedule_associated(incall, schedule):
    with a.incall_schedule(incall, schedule, check=False):
        response = confd.incalls(incall['id']).delete()
        response.assert_deleted()


@fixtures.incall()
@fixtures.schedule()
def test_delete_schedule_when_incall_and_schedule_associated(incall, schedule):
    with a.incall_schedule(incall, schedule, check=False):
        response = confd.schedules(schedule['id']).delete()
        response.assert_deleted()
