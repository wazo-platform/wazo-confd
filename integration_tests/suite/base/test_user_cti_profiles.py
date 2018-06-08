# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import re

from hamcrest import assert_that, has_entries

from . import confd
from ..helpers import fixtures
from ..helpers import errors as e
from ..helpers import associations as a
from ..helpers import scenarios as s


FAKE_ID = 999999999

missing_username_password_regex = re.compile(r"User must have a username and password to enable a CtiProfile")


def test_get_when_user_does_not_exist():
    response = confd.users(FAKE_ID).cti.get()
    response.assert_match(404, e.not_found('User'))


@fixtures.user()
def test_associate_user_with_fake_cti_profile(user):
    url = confd.users(user['id']).cti
    response = url.put(cti_profile_id=FAKE_ID)
    response.assert_match(400, e.not_found('CtiProfile'))


@fixtures.user()
def test_associate_user_with_0_cti_profile(user):
    url = confd.users(user['id']).cti
    response = url.put(cti_profile_id=0)
    response.assert_match(400, e.not_found('CtiProfile'))


@fixtures.user(username=None, password=None)
def test_enable_cti_for_user_without_username_or_password(user):
    url = confd.users(user['id']).cti
    response = url.put(enabled=True)
    response.assert_match(400, missing_username_password_regex)


@fixtures.cti_profile()
@fixtures.user()
def test_associate_user_with_null_cti_profile(cti_profile, user):
    response = confd.users(user['id']).cti.put(cti_profile_id=cti_profile['id'])
    response.assert_updated()
    response = confd.users(user['id']).cti.get()
    assert_that(response.item, has_entries(user_id=user['id'],
                                           cti_profile_id=cti_profile['id']))

    response = confd.users(user['id']).cti.put(cti_profile_id=None)
    response.assert_updated()
    response = confd.users(user['id']).cti.get()
    assert_that(response.item, has_entries(user_id=user['id'],
                                           cti_profile_id=None))


@fixtures.user()
def test_get_user_cti_profile_when_not_associated(user):
    response = confd.users(user['id']).cti.get()

    response.assert_link('users')
    assert_that(response.item, has_entries(user_id=user['id'],
                                           cti_profile_id=None,
                                           enabled=False))


@fixtures.cti_profile()
@fixtures.user(username="username", password="password")
def test_associate_user_with_cti_profile(cti_profile, user):
    response = confd.users(user['id']).cti.put(cti_profile_id=cti_profile['id'])
    response.assert_updated()


@fixtures.cti_profile()
@fixtures.user(username="username", password="password")
def test_associate_using_uuid(cti_profile, user):
    response = confd.users(user['uuid']).cti.put(cti_profile_id=cti_profile['id'])
    response.assert_updated()


@fixtures.cti_profile()
@fixtures.user(username="username", password="password")
def test_get_user_cti_profile_when_associated(cti_profile, user):
    with a.user_cti_profile(user, cti_profile):
        response = confd.users(user['id']).cti.get()

        response.assert_link('users')
        response.assert_link('cti_profiles')
        assert_that(response.item, has_entries(user_id=user['id'],
                                               cti_profile_id=cti_profile['id'],
                                               enabled=True))


@fixtures.cti_profile()
@fixtures.user(username="username", password="password")
def test_get_association_using_uuid(cti_profile, user):
    with a.user_cti_profile(user, cti_profile):
        response = confd.users(user['uuid']).cti.get()
        assert_that(response.item, has_entries(cti_profile_id=cti_profile['id'],
                                               user_id=user['id']))


@fixtures.cti_profile(name='my-profile')
@fixtures.user(username="username", password="password")
def test_get_cti_profile_associated_to_user(cti_profile, user):
    with a.user_cti_profile(user, cti_profile):
        response = confd.users(user['uuid']).get()

        assert_that(response.item, has_entries(
            cti_profile=has_entries(
                id=cti_profile['id'],
                name=cti_profile['name']
            )
        ))


@fixtures.cti_profile()
@fixtures.user()
def test_bus_events(cti_profile, user):
    yield (s.check_bus_event,
           'config.user_cti_profile_association.edited',
           confd.users(user['uuid']).cti.put, {'cti_profile_id': cti_profile['id']})
