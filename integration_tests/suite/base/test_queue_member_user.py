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


@fixtures.queue()
@fixtures.user()
def test_associate_errors(queue, user):
    fake_queue = confd.queues(FAKE_ID).members.users(user['id']).put
    fake_user = confd.queues(queue['id']).members.users(FAKE_UUID).put

    yield s.check_resource_not_found, fake_queue, 'Queue'
    yield s.check_resource_not_found, fake_user, 'User'

    url = confd.queues(queue['id']).members.users(user['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'priority', -1
    yield s.check_bogus_field_returns_error, url, 'priority', None
    yield s.check_bogus_field_returns_error, url, 'priority', 'string'
    yield s.check_bogus_field_returns_error, url, 'priority', []
    yield s.check_bogus_field_returns_error, url, 'priority', {}


@fixtures.queue()
@fixtures.user()
def test_dissociate_errors(queue, user):
    fake_queue = confd.queues(FAKE_ID).members.users(user['id']).delete
    fake_user = confd.queues(queue['id']).members.users(FAKE_UUID).delete

    yield s.check_resource_not_found, fake_queue, 'Queue'
    yield s.check_resource_not_found, fake_user, 'User'


@fixtures.queue()
@fixtures.user()
@fixtures.line_sip()
def test_associate(queue, user, line):
    with a.user_line(user, line):
        response = confd.queues(queue['id']).members.users(user['id']).put(priority=42)
        response.assert_updated()


@fixtures.queue()
@fixtures.user()
@fixtures.line_sip()
def test_update_properties(queue, user, line):
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


@fixtures.queue()
@fixtures.user()
@fixtures.line_sip()
def test_associate_already_associated(queue, user, line):
    with a.user_line(user, line):
        with a.queue_member_user(queue, user):
            response = confd.queues(queue['id']).members.users(user['id']).put()
            response.assert_updated()


@fixtures.queue()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
def test_associate_multiple_user_with_same_line(queue, user1, user2, line):
    with a.user_line(user1, line), a.user_line(user2, line):
        with a.queue_member_user(queue, user1):
            response = confd.queues(queue['id']).members.users(user2['id']).put()
            response.assert_match(400, re.compile('Cannot associate different users with the same line'))


@fixtures.queue()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multiple_users_to_queue(queue, user1, user2, line1, line2):
    with a.user_line(user1, line1), a.user_line(user2, line2):
        with a.queue_member_user(queue, user1):
            response = confd.queues(queue['id']).members.users(user2['id']).put()
            response.assert_updated()


@fixtures.queue()
@fixtures.queue()
@fixtures.user()
@fixtures.line_sip()
def test_associate_multiple_queues_to_user(queue1, queue2, user, line):
    with a.user_line(user, line):
        with a.queue_member_user(queue1, user):
            response = confd.queues(queue2['id']).members.users(user['id']).put()
            response.assert_updated()


@fixtures.queue(wazo_tenant=MAIN_TENANT)
@fixtures.queue(wazo_tenant=SUB_TENANT)
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_queue, sub_queue, main_user, sub_user):
    response = confd.queues(main_queue['id']).members.users(main_user['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Queue'))

    response = confd.queues(sub_queue['id']).members.users(main_user['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('User'))

    response = confd.queues(main_queue['id']).members.users(sub_user['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())


@fixtures.queue()
@fixtures.user()
@fixtures.line_sip()
def test_dissociate(queue, user, line):
    with a.user_line(user, line):
        with a.queue_member_user(queue, user, check=False):
            response = confd.queues(queue['id']).members.users(user['id']).delete()
            response.assert_deleted()


@fixtures.queue()
@fixtures.user()
@fixtures.line_sip()
def test_dissociate_not_associated(queue, user, line):
    with a.user_line(user, line):
        response = confd.queues(queue['id']).members.users(user['id']).delete()
        response.assert_deleted()


@fixtures.queue(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.line_sip(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(queue, user, line):
    with a.user_line(user, line):
        response = confd.queues(queue['id']).members.users(user['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Queue'))


@fixtures.queue()
@fixtures.user()
@fixtures.line_sip()
def test_get_queue_relation(queue, user, line):
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


@fixtures.queue()
@fixtures.user()
@fixtures.line_sip()
def test_get_user_relation(queue, user, line):
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


@fixtures.queue()
@fixtures.user()
@fixtures.line_sip()
def test_delete_queue_when_queue_and_user_associated(queue, user, line):
    with a.user_line(user, line):
        with a.queue_member_user(queue, user, check=False):
            response = confd.queues(queue['id']).delete()
            response.assert_deleted()


@fixtures.queue()
@fixtures.user()
@fixtures.line_sip()
def test_delete_user_when_queue_and_user_associated(queue, user, line):
    with a.user_line(user, line, check=False):
        with a.queue_member_user(queue, user, check=False):
            confd.lines(line['id']).delete().assert_deleted()
            response = confd.users(user['id']).delete()
            response.assert_deleted()


@fixtures.queue()
@fixtures.user()
@fixtures.line_sip()
def test_bus_events(queue, user, line):
    with a.user_line(user, line):
        url = confd.queues(queue['id']).members.users(user['uuid'])
        yield s.check_bus_event, 'config.user_queue_association.created', url.put
        yield s.check_bus_event, 'config.user_queue_association.deleted', url.delete
