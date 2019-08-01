# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

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
FAKE_UUID = '99999999-9999-9999-9999-999999999999'


def test_associate_errors():
    with fixtures.queue() as queue, fixtures.user() as user:
        fake_queue = confd.queues(FAKE_ID).members.users(user['id']).put
        fake_user = confd.queues(queue['id']).members.users(FAKE_UUID).put

        s.check_resource_not_found(fake_queue, 'Queue')
        s.check_resource_not_found(fake_user, 'User')

        url = confd.queues(queue['id']).members.users(user['id']).put
        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'priority', -1)
    s.check_bogus_field_returns_error(url, 'priority', None)
    s.check_bogus_field_returns_error(url, 'priority', 'string')
    s.check_bogus_field_returns_error(url, 'priority', [])
    s.check_bogus_field_returns_error(url, 'priority', {})


def test_dissociate_errors():
    with fixtures.queue() as queue, fixtures.user() as user:
        fake_queue = confd.queues(FAKE_ID).members.users(user['id']).delete
        fake_user = confd.queues(queue['id']).members.users(FAKE_UUID).delete

        s.check_resource_not_found(fake_queue, 'Queue')
        s.check_resource_not_found(fake_user, 'User')



def test_associate():
    with fixtures.queue() as queue, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            response = confd.queues(queue['id']).members.users(user['id']).put(priority=42)
            response.assert_updated()


def test_update_properties():
    with fixtures.queue() as queue, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            with a.queue_member_user(queue, user, priority=0):
                response = confd.queues(queue['id']).members.users(user['id']).put(priority=42)
                response.assert_updated()

                response = confd.queues(queue['id']).get()
                assert_that(response.item, has_entries(
                    members=has_entries(
                        users=contains(has_entries(
                            priority=42,
                        ))
                    )
                ))


def test_associate_already_associated():
    with fixtures.queue() as queue, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            with a.queue_member_user(queue, user):
                response = confd.queues(queue['id']).members.users(user['id']).put()
                response.assert_updated()


def test_associate_multiple_user_with_same_line():
    with fixtures.queue() as queue, fixtures.user() as user1, fixtures.user() as user2, fixtures.line_sip() as line:
        with a.user_line(user1, line), a.user_line(user2, line):
            with a.queue_member_user(queue, user1):
                response = confd.queues(queue['id']).members.users(user2['id']).put()
                response.assert_match(400, re.compile('Cannot associate different users with the same line'))


def test_associate_multiple_users_to_queue():
    with fixtures.queue() as queue, fixtures.user() as user1, fixtures.user() as user2, fixtures.line_sip() as line1, fixtures.line_sip() as line2:
        with a.user_line(user1, line1), a.user_line(user2, line2):
            with a.queue_member_user(queue, user1):
                response = confd.queues(queue['id']).members.users(user2['id']).put()
                response.assert_updated()


def test_associate_multiple_queues_to_user():
    with fixtures.queue() as queue1, fixtures.queue() as queue2, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            with a.queue_member_user(queue1, user):
                response = confd.queues(queue2['id']).members.users(user['id']).put()
                response.assert_updated()


def test_associate_multi_tenant():
    with fixtures.queue(wazo_tenant=MAIN_TENANT) as main_queue, fixtures.queue(wazo_tenant=SUB_TENANT) as sub_queue, fixtures.user(wazo_tenant=MAIN_TENANT) as main_user, fixtures.user(wazo_tenant=SUB_TENANT) as sub_user:
        response = confd.queues(main_queue['id']).members.users(main_user['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Queue'))

        response = confd.queues(sub_queue['id']).members.users(main_user['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('User'))

        response = confd.queues(main_queue['id']).members.users(sub_user['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.queue() as queue, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            with a.queue_member_user(queue, user, check=False):
                response = confd.queues(queue['id']).members.users(user['id']).delete()
                response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.queue() as queue, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            response = confd.queues(queue['id']).members.users(user['id']).delete()
            response.assert_deleted()


def test_dissociate_multi_tenant():
    with fixtures.queue(wazo_tenant=MAIN_TENANT) as queue, fixtures.user(wazo_tenant=MAIN_TENANT) as user, fixtures.line_sip(wazo_tenant=SUB_TENANT) as line:
        with a.user_line(user, line):
            response = confd.queues(queue['id']).members.users(user['id']).delete(wazo_tenant=SUB_TENANT)
            response.assert_match(404, e.not_found('Queue'))


def test_get_queue_relation():
    with fixtures.queue() as queue, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            with a.queue_member_user(queue, user, priority=0):
                response = confd.queues(queue['id']).get()
                assert_that(response.item, has_entries(
                    members=has_entries(
                        users=contains(
                            has_entries(
                                uuid=user['uuid'],
                                firstname=user['firstname'],
                                lastname=user['lastname'],
                                priority=0,
                                links=user['links'],
                            )
                        )
                    )
                ))


def test_get_user_relation():
    with fixtures.queue() as queue, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            with a.queue_member_user(queue, user):
                response = confd.users(user['id']).get()
                assert_that(response.item, has_entries(
                    queues=contains(
                        has_entries(
                            id=queue['id'],
                            name=queue['name'],
                            label=queue['label'],
                            links=queue['links'],
                        )
                    )
                ))


def test_delete_queue_when_queue_and_user_associated():
    with fixtures.queue() as queue, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            with a.queue_member_user(queue, user, check=False):
                response = confd.queues(queue['id']).delete()
                response.assert_deleted()


def test_delete_user_when_queue_and_user_associated():
    with fixtures.queue() as queue, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line, check=False):
            with a.queue_member_user(queue, user, check=False):
                confd.lines(line['id']).delete().assert_deleted()
                response = confd.users(user['id']).delete()
                response.assert_deleted()


def test_bus_events():
    with fixtures.queue() as queue, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            url = confd.queues(queue['id']).members.users(user['uuid'])
            s.check_bus_event('config.user_queue_association.created', url.put)
            s.check_bus_event('config.user_queue_association.deleted', url.delete)
