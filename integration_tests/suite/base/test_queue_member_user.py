# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd
from ..helpers import (
    associations as a,
    fixtures,
    scenarios as s,
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
