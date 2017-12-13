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


@fixtures.user()
@fixtures.schedule()
def test_associate_errors(user, schedule):
    fake_user = confd.users(FAKE_ID).schedules(schedule['id']).put
    fake_schedule = confd.users(user['uuid']).schedules(FAKE_ID).put

    yield s.check_resource_not_found, fake_user, 'User'
    yield s.check_resource_not_found, fake_schedule, 'Schedule'


@fixtures.user()
@fixtures.schedule()
def test_dissociate_errors(user, schedule):
    fake_user = confd.users(FAKE_ID).schedules(schedule['id']).delete
    fake_schedule = confd.users(user['uuid']).schedules(FAKE_ID).delete

    yield s.check_resource_not_found, fake_user, 'User'
    yield s.check_resource_not_found, fake_schedule, 'Schedule'


@fixtures.user()
@fixtures.schedule()
def test_associate(user, schedule):
    response = confd.users(user['uuid']).schedules(schedule['id']).put()
    response.assert_updated()


@fixtures.user()
@fixtures.schedule()
def test_associate_with_user_id(user, schedule):
    response = confd.users(user['id']).schedules(schedule['id']).put()
    response.assert_updated()


@fixtures.user()
@fixtures.schedule()
def test_associate_already_associated(user, schedule):
    with a.user_schedule(user, schedule):
        response = confd.users(user['uuid']).schedules(schedule['id']).put()
        response.assert_updated()


@fixtures.user()
@fixtures.schedule()
@fixtures.schedule()
def test_associate_multiple_schedules_to_user(user, schedule1, schedule2):
    with a.user_schedule(user, schedule1):
        response = confd.users(user['uuid']).schedules(schedule2['id']).put()
        response.assert_match(400, e.resource_associated('User', 'Schedule'))


@fixtures.user()
@fixtures.user()
@fixtures.schedule()
def test_associate_multiple_users_to_schedule(user1, user2, schedule):
    with a.user_schedule(user1, schedule):
        response = confd.users(user2['id']).schedules(schedule['id']).put()
        response.assert_updated()


@fixtures.user()
@fixtures.schedule()
def test_dissociate(user, schedule):
    with a.user_schedule(user, schedule, check=False):
        response = confd.users(user['uuid']).schedules(schedule['id']).delete()
        response.assert_deleted()


@fixtures.user()
@fixtures.schedule()
def test_dissociate_not_associated(user, schedule):
    response = confd.users(user['uuid']).schedules(schedule['id']).delete()
    response.assert_deleted()


@fixtures.user()
@fixtures.schedule()
def test_get_user_relation(user, schedule):
    with a.user_schedule(user, schedule):
        response = confd.users(user['uuid']).get()
        assert_that(response.item, has_entries(
            schedules=contains(has_entries(id=schedule['id'],
                                           name=schedule['name']))
        ))


@fixtures.schedule()
@fixtures.user()
def test_get_schedule_relation(schedule, user):
    with a.user_schedule(user, schedule):
        response = confd.schedules(schedule['id']).get()
        assert_that(response.item, has_entries(
            users=contains(has_entries(uuid=user['uuid']))
        ))


@fixtures.user()
@fixtures.schedule()
def test_delete_user_when_user_and_schedule_associated(user, schedule):
    with a.user_schedule(user, schedule, check=False):
        response = confd.users(user['uuid']).delete()
        response.assert_deleted()


@fixtures.user()
@fixtures.schedule()
def test_delete_schedule_when_user_and_schedule_associated(user, schedule):
    with a.user_schedule(user, schedule, check=False):
        response = confd.schedules(schedule['id']).delete()
        response.assert_deleted()
