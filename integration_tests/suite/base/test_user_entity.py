# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    empty,
    has_entries,
    not_,
)

from ..helpers import scenarios as s
from ..helpers import fixtures
from . import confd

FAKE_ID = 999999999


def test_get_errors():
    fake_user = confd.users(FAKE_ID).entities.get
    yield s.check_resource_not_found, fake_user, 'User'


@fixtures.user()
def test_get_entities_associated_to_user(user):
    expected = has_entries({'user_id': user['id'],
                            'entity_id': not_(empty())})

    response = confd.users(user['id']).entities.get()
    assert_that(response.item, expected)


@fixtures.user()
def test_delete_user_when_user_and_entity_associated(user):
    response = confd.users(user['id']).entities.get()
    assert_that(response.item, not_(empty()))

    confd.users(user['id']).delete().assert_deleted()
    invalid_user = confd.users(user['id']).entities.get
    s.check_resource_not_found(invalid_user, 'User')
