# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from test_api import scenarios as s
from test_api import confd
from test_api import errors as e
from test_api import fixtures
from test_api import associations as a


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
