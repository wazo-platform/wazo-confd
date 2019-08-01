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
    with fixtures.user() as user, fixtures.schedule() as schedule:
        fake_user = confd.users(FAKE_ID).schedules(schedule['id']).put
        fake_schedule = confd.users(user['uuid']).schedules(FAKE_ID).put

        s.check_resource_not_found(fake_user, 'User')
        s.check_resource_not_found(fake_schedule, 'Schedule')



def test_dissociate_errors():
    with fixtures.user() as user, fixtures.schedule() as schedule:
        fake_user = confd.users(FAKE_ID).schedules(schedule['id']).delete
        fake_schedule = confd.users(user['uuid']).schedules(FAKE_ID).delete

        s.check_resource_not_found(fake_user, 'User')
        s.check_resource_not_found(fake_schedule, 'Schedule')



def test_associate():
    with fixtures.user() as user, fixtures.schedule() as schedule:
        response = confd.users(user['uuid']).schedules(schedule['id']).put()
        response.assert_updated()



def test_associate_with_user_id():
    with fixtures.user() as user, fixtures.schedule() as schedule:
        response = confd.users(user['id']).schedules(schedule['id']).put()
        response.assert_updated()



def test_associate_already_associated():
    with fixtures.user() as user, fixtures.schedule() as schedule:
        with a.user_schedule(user, schedule):
            response = confd.users(user['uuid']).schedules(schedule['id']).put()
            response.assert_updated()


def test_associate_multiple_schedules_to_user():
    with fixtures.user() as user, fixtures.schedule() as schedule1, fixtures.schedule() as schedule2:
        with a.user_schedule(user, schedule1):
            response = confd.users(user['uuid']).schedules(schedule2['id']).put()
            response.assert_match(400, e.resource_associated('User', 'Schedule'))


def test_associate_multiple_users_to_schedule():
    with fixtures.user() as user1, fixtures.user() as user2, fixtures.schedule() as schedule:
        with a.user_schedule(user1, schedule):
            response = confd.users(user2['id']).schedules(schedule['id']).put()
            response.assert_updated()


def test_associate_multi_tenant():
    with fixtures.user(wazo_tenant=MAIN_TENANT) as main_user, fixtures.user(wazo_tenant=SUB_TENANT) as sub_user, fixtures.schedule(wazo_tenant=MAIN_TENANT) as main_schedule, fixtures.schedule(wazo_tenant=SUB_TENANT) as sub_schedule:
        response = confd.users(main_user['uuid']).schedules(sub_schedule['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('User'))

        response = confd.users(sub_user['uuid']).schedules(main_schedule['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Schedule'))

        response = confd.users(main_user['uuid']).schedules(sub_schedule['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.user() as user, fixtures.schedule() as schedule:
        with a.user_schedule(user, schedule, check=False):
            response = confd.users(user['uuid']).schedules(schedule['id']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.user() as user, fixtures.schedule() as schedule:
        response = confd.users(user['uuid']).schedules(schedule['id']).delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.user(wazo_tenant=MAIN_TENANT) as main_user, fixtures.user(wazo_tenant=SUB_TENANT) as sub_user, fixtures.schedule(wazo_tenant=MAIN_TENANT) as main_schedule, fixtures.schedule(wazo_tenant=SUB_TENANT) as sub_schedule:
        response = confd.users(main_user['uuid']).schedules(sub_schedule['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('User'))

        response = confd.users(sub_user['uuid']).schedules(main_schedule['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Schedule'))



def test_get_user_relation():
    with fixtures.user() as user, fixtures.schedule() as schedule:
        with a.user_schedule(user, schedule):
            response = confd.users(user['uuid']).get()
            assert_that(response.item, has_entries(
                schedules=contains(has_entries(id=schedule['id'],
                                               name=schedule['name']))
            ))


def test_get_schedule_relation():
    with fixtures.schedule() as schedule, fixtures.user() as user:
        with a.user_schedule(user, schedule):
            response = confd.schedules(schedule['id']).get()
            assert_that(response.item, has_entries(
                users=contains(has_entries(uuid=user['uuid']))
            ))


def test_delete_user_when_user_and_schedule_associated():
    with fixtures.user() as user, fixtures.schedule() as schedule:
        with a.user_schedule(user, schedule, check=False):
            response = confd.users(user['uuid']).delete()
            response.assert_deleted()


def test_delete_schedule_when_user_and_schedule_associated():
    with fixtures.user() as user, fixtures.schedule() as schedule:
        with a.user_schedule(user, schedule, check=False):
            response = confd.schedules(schedule['id']).delete()
            response.assert_deleted()
