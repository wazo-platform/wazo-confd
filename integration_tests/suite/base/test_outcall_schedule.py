# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (assert_that,
                      contains,
                      has_entries)
from ..helpers import scenarios as s
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import associations as a
from . import confd

FAKE_ID = 999999999


@fixtures.outcall()
@fixtures.schedule()
def test_associate_errors(outcall, schedule):
    fake_outcall = confd.outcalls(FAKE_ID).schedules(schedule['id']).put
    fake_schedule = confd.outcalls(outcall['id']).schedules(FAKE_ID).put

    yield s.check_resource_not_found, fake_outcall, 'Outcall'
    yield s.check_resource_not_found, fake_schedule, 'Schedule'


@fixtures.outcall()
@fixtures.schedule()
def test_dissociate_errors(outcall, schedule):
    fake_outcall = confd.outcalls(FAKE_ID).schedules(schedule['id']).delete
    fake_schedule = confd.outcalls(outcall['id']).schedules(FAKE_ID).delete

    yield s.check_resource_not_found, fake_outcall, 'Outcall'
    yield s.check_resource_not_found, fake_schedule, 'Schedule'


@fixtures.outcall()
@fixtures.schedule()
def test_associate(outcall, schedule):
    response = confd.outcalls(outcall['id']).schedules(schedule['id']).put()
    response.assert_updated()


@fixtures.outcall()
@fixtures.schedule()
def test_associate_already_associated(outcall, schedule):
    with a.outcall_schedule(outcall, schedule):
        response = confd.outcalls(outcall['id']).schedules(schedule['id']).put()
        response.assert_updated()


@fixtures.outcall()
@fixtures.schedule()
@fixtures.schedule()
def test_associate_multiple_schedules_to_outcall(outcall, schedule1, schedule2):
    with a.outcall_schedule(outcall, schedule1):
        response = confd.outcalls(outcall['id']).schedules(schedule2['id']).put()
        response.assert_match(400, e.resource_associated('Outcall', 'Schedule'))


@fixtures.outcall()
@fixtures.outcall()
@fixtures.schedule()
def test_associate_multiple_outcalls_to_schedule(outcall1, outcall2, schedule):
    with a.outcall_schedule(outcall1, schedule):
        response = confd.outcalls(outcall2['id']).schedules(schedule['id']).put()
        response.assert_updated()


@fixtures.outcall()
@fixtures.schedule()
def test_dissociate(outcall, schedule):
    with a.outcall_schedule(outcall, schedule, check=False):
        response = confd.outcalls(outcall['id']).schedules(schedule['id']).delete()
        response.assert_deleted()


@fixtures.outcall()
@fixtures.schedule()
def test_dissociate_not_associated(outcall, schedule):
    response = confd.outcalls(outcall['id']).schedules(schedule['id']).delete()
    response.assert_deleted()


@fixtures.outcall()
@fixtures.schedule()
def test_get_outcall_relation(outcall, schedule):
    with a.outcall_schedule(outcall, schedule):
        response = confd.outcalls(outcall['id']).get()
        assert_that(response.item, has_entries(
            schedules=contains(has_entries(id=schedule['id'],
                                           name=schedule['name']))
        ))


@fixtures.schedule()
@fixtures.outcall()
def test_get_schedule_relation(schedule, outcall):
    with a.outcall_schedule(outcall, schedule):
        response = confd.schedules(schedule['id']).get()
        assert_that(response.item, has_entries(
            outcalls=contains(has_entries(id=outcall['id']))
        ))


@fixtures.outcall()
@fixtures.schedule()
def test_delete_outcall_when_outcall_and_schedule_associated(outcall, schedule):
    with a.outcall_schedule(outcall, schedule, check=False):
        response = confd.outcalls(outcall['id']).delete()
        response.assert_deleted()


@fixtures.outcall()
@fixtures.schedule()
def test_delete_schedule_when_outcall_and_schedule_associated(outcall, schedule):
    with a.outcall_schedule(outcall, schedule, check=False):
        response = confd.schedules(schedule['id']).delete()
        response.assert_deleted()
