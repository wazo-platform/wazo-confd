# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      contains_inanyorder,
                      empty,
                      has_entries)

from ..test_api import scenarios as s
from . import confd
from ..test_api import fixtures
from ..test_api import associations as a


FAKE_ID = 999999999
FAKE_UUID = '99999999-9999-9999-9999-999999999999'


@fixtures.paging()
@fixtures.user()
def test_associate_errors(paging, user):
    response = confd.pagings(FAKE_ID).members.users.put(users=[user])
    response.assert_status(404)

    url = confd.pagings(paging['id']).members.users.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'users', 123
    yield s.check_bogus_field_returns_error, url, 'users', None
    yield s.check_bogus_field_returns_error, url, 'users', True
    yield s.check_bogus_field_returns_error, url, 'users', 'string'
    yield s.check_bogus_field_returns_error, url, 'users', [123]
    yield s.check_bogus_field_returns_error, url, 'users', [None]
    yield s.check_bogus_field_returns_error, url, 'users', ['string']
    yield s.check_bogus_field_returns_error, url, 'users', [{}]
    yield s.check_bogus_field_returns_error, url, 'users', [{'uuid': None}]
    yield s.check_bogus_field_returns_error, url, 'users', [{'uuid': 1}, {'uuid': None}]
    yield s.check_bogus_field_returns_error, url, 'users', [{'not_uuid': 123}]
    yield s.check_bogus_field_returns_error, url, 'users', [{'uuid': FAKE_UUID}]


@fixtures.paging()
@fixtures.user()
def test_associate(paging, user):
    response = confd.pagings(paging['id']).members.users.put(users=[user])
    response.assert_updated()


@fixtures.paging()
@fixtures.user()
@fixtures.user()
@fixtures.user()
def test_associate_multiple(paging, user1, user2, user3):
    response = confd.pagings(paging['id']).members.users.put(users=[user1, user2, user3])
    response.assert_updated()

    response = confd.pagings(paging['id']).get()
    assert_that(response.item, has_entries(
        members=has_entries(users=contains_inanyorder(has_entries(uuid=user1['uuid']),
                                                      has_entries(uuid=user2['uuid']),
                                                      has_entries(uuid=user3['uuid'])))
    ))


@fixtures.paging()
@fixtures.user()
def test_associate_same_user(paging, user):
    response = confd.pagings(paging['id']).members.users.put(users=[user, user])
    response.assert_status(400)


@fixtures.paging()
@fixtures.user()
@fixtures.user()
def test_get_users_associated_to_paging(paging, user1, user2):
    with a.paging_member_user(paging, user2, user1):
        response = confd.pagings(paging['id']).get()
        assert_that(response.item, has_entries(
            members=has_entries(users=contains_inanyorder(
                has_entries(uuid=user2['uuid'],
                            firstname=user2['firstname'],
                            lastname=user2['lastname']),
                has_entries(uuid=user1['uuid'],
                            firstname=user1['firstname'],
                            lastname=user1['lastname']))
            )
        ))


@fixtures.paging()
@fixtures.user()
@fixtures.user()
def test_dissociate(paging, user1, user2):
    with a.paging_member_user(paging, user1, user2):
        response = confd.pagings(paging['id']).members.users.put(users=[])
        response.assert_updated()


@fixtures.paging()
@fixtures.user()
@fixtures.user()
def test_delete_paging_when_paging_and_user_associated(paging, user1, user2):
    with a.paging_member_user(paging, user1, user2, check=False):
        confd.pagings(paging['id']).delete().assert_deleted()

        deleted_paging = confd.pagings(paging['id']).get
        yield s.check_resource_not_found, deleted_paging, 'Paging'

        # When the relation will be added,
        # we should check if users have the key pagings to empty


@fixtures.paging()
@fixtures.paging()
@fixtures.user()
def test_delete_user_when_paging_and_user_associated(paging1, paging2, user):
    with a.paging_member_user(paging1, user, check=False), a.paging_member_user(paging2, user, check=False):
        confd.users(user['uuid']).delete().assert_deleted()

        response = confd.pagings(paging1['id']).get()
        yield assert_that, response.item['members']['users'], empty()

        response = confd.pagings(paging2['id']).get()
        yield assert_that, response.item['members']['users'], empty()


@fixtures.paging()
@fixtures.user()
def test_bus_events(paging, user):
    url = confd.pagings(paging['id']).members.users.put
    body = {'users': [user]}
    yield s.check_bus_event, 'config.pagings.members.users.updated', url, body
