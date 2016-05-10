# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from hamcrest import (assert_that,
                      empty,
                      has_entries,
                      not_)

from test_api import scenarios as s
from test_api import confd
from test_api import errors as e
from test_api import fixtures
from test_api import associations as a


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
def test_delete_user_when_user_and_entity_associated(entity, user):
    with a.user_entity(user, entity, check=False):
        response = confd.users(user['id']).entities.get()
        assert_that(response.item, not_(empty()))
        confd.users(user['id']).delete().assert_deleted()
        invalid_user = confd.users(user['id']).entities.get
        yield s.check_resource_not_found, invalid_user, 'User'
