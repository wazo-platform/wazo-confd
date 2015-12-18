# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

import re

from hamcrest import assert_that, has_entries

from test_api import confd
from test_api import fixtures
from test_api import errors as e
from test_api import associations as a


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


@fixtures.user(username=None, password=None)
def test_enable_cti_for_user_without_username_or_password(user):
    url = confd.users(user['id']).cti
    response = url.put(enabled=True)
    response.assert_match(400, missing_username_password_regex)


@fixtures.user()
def test_get_user_cti_profile_when_not_associated(user):
    response = confd.users(user['id']).cti.get()

    response.assert_link('users')
    assert_that(response.item, has_entries(user_id=user['id'],
                                           cti_profile_id=None,
                                           enabled=False))


@fixtures.user(username="username", password="password")
@fixtures.cti_profile("Client")
def test_associate_user_with_cti_profile(user, cti_profile):
    response = confd.users(user['id']).cti.put(cti_profile_id=cti_profile['id'])
    response.assert_updated()


@fixtures.user(username="username", password="password")
@fixtures.cti_profile("Client")
def test_associate_using_uuid(user, cti_profile):
    response = confd.users(user['uuid']).cti.put(cti_profile_id=cti_profile['id'])
    response.assert_updated()


@fixtures.user(username="username", password="password")
@fixtures.cti_profile("Client")
def test_get_user_cti_profile_when_associated(user, cti_profile):
    with a.user_cti_profile(user, cti_profile):
        response = confd.users(user['id']).cti.get()

        response.assert_link('users')
        response.assert_link('cti_profiles')
        assert_that(response.item, has_entries(user_id=user['id'],
                                               cti_profile_id=cti_profile['id'],
                                               enabled=True))


@fixtures.user(username="username", password="password")
@fixtures.cti_profile("Client")
def test_get_association_using_uuid(user, cti_profile):
    with a.user_cti_profile(user, cti_profile):
        response = confd.users(user['uuid']).cti.get()
        assert_that(response.item, has_entries(cti_profile_id=cti_profile['id'],
                                               user_id=user['id']))
