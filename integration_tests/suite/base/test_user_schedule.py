# -*- coding: utf-8 -*-
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


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
@fixtures.schedule(wazo_tenant=MAIN_TENANT)
@fixtures.schedule(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_user, sub_user, main_schedule, sub_schedule):
    response = confd.users(main_user['uuid']).schedules(sub_schedule['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('User'))

    response = confd.users(sub_user['uuid']).schedules(main_schedule['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Schedule'))

    response = confd.users(main_user['uuid']).schedules(sub_schedule['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())


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


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
@fixtures.schedule(wazo_tenant=MAIN_TENANT)
@fixtures.schedule(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(main_user, sub_user, main_schedule, sub_schedule):
    response = confd.users(main_user['uuid']).schedules(sub_schedule['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('User'))

    response = confd.users(sub_user['uuid']).schedules(main_schedule['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Schedule'))


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
