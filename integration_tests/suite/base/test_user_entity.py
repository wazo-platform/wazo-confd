# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      empty,
                      has_entries,
                      not_)

from ..helpers import scenarios as s
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import associations as a
from . import confd

FAKE_ID = 999999999


@fixtures.entity()
@fixtures.user()
def test_associate_errors(entity, user):
    fake_user = confd.users(FAKE_ID).entities(entity['id']).put
    fake_entity = confd.users(user['id']).entities(FAKE_ID).put

    yield s.check_resource_not_found, fake_user, 'User'
    yield s.check_resource_not_found, fake_entity, 'Entity'


def test_get_errors():
    fake_user = confd.users(FAKE_ID).entities.get
    yield s.check_resource_not_found, fake_user, 'User'


@fixtures.entity()
@fixtures.user()
def test_associate_user_entity(entity, user):
    response = confd.users(user['id']).entities(entity['id']).put()
    response.assert_updated()


@fixtures.entity()
@fixtures.user()
def test_associate_using_uuid(entity, user):
    response = confd.users(user['uuid']).entities(entity['id']).put()
    response.assert_updated()


@fixtures.entity()
@fixtures.user()
def test_get_entities_associated_to_user(entity, user):
    expected = has_entries({'user_id': user['id'],
                            'entity_id': entity['id']})

    with a.user_entity(user, entity):
        response = confd.users(user['id']).entities.get()
        assert_that(response.item, expected)

        response = confd.users(user['uuid']).entities.get()
        assert_that(response.item, expected)


@fixtures.entity()
@fixtures.entity()
@fixtures.user()
def test_associate_when_user_already_associated_to_other_entity(entity1, entity2, user):
    with a.user_entity(user, entity1):
        response = confd.users(user['id']).entities(entity2['id']).put()
        response.assert_updated()


@fixtures.entity()
@fixtures.user()
def test_associate_when_user_already_associated_to_same_entity(entity, user):
    with a.user_entity(user, entity):
        response = confd.users(user['id']).entities(entity['id']).put()
        response.assert_match(400, e.resource_associated('User', 'Entity'))


@fixtures.entity()
@fixtures.user()
@fixtures.line_sip()
def test_associate_when_user_already_associated_to_a_line(entity, user, line):
    with a.user_line(user, line):
        response = confd.users(user['id']).entities(entity['id']).put()
        response.assert_match(400, e.resource_associated('User', 'Line'))


@fixtures.entity()
@fixtures.user()
def test_delete_user_when_user_and_entity_associated(entity, user):
    with a.user_entity(user, entity, check=False):
        response = confd.users(user['id']).entities.get()
        assert_that(response.item, not_(empty()))
        confd.users(user['id']).delete().assert_deleted()
        invalid_user = confd.users(user['id']).entities.get
        s.check_resource_not_found(invalid_user, 'User')


@fixtures.entity()
@fixtures.user()
def test_bus_events(entity, user):
    url = confd.users(user['id']).entities(entity['id'])
    yield s.check_bus_event, 'config.users.{}.entities.updated'.format(user['uuid']), url.put
