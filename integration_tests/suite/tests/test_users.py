# -*- coding: utf-8 -*-

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

from __future__ import unicode_literals


from test_api import scenarios as s
from test_api import errors as e
from test_api import associations as a
from test_api import confd
from test_api import fixtures
from test_api.helpers.user import generate_user

from hamcrest import assert_that, equal_to, has_entries, has_entry, has_item

FIELDS = ['firstname',
          'lastname',
          'timezone',
          'language',
          'description',
          'caller_id',
          'outgoing_caller_id',
          'mobile_phone_number',
          'username',
          'password',
          'music_on_hold',
          'preprocess_subroutine',
          'userfield']

REQUIRED = ['firstname']

BOGUS = [(f, 123, 'unicode string') for f in FIELDS]

NULL_USER = {"firstname": "Jôhn",
             "lastname": None,
             "username": None,
             "mobile_phone_number": None,
             "userfield": None,
             "outgoing_caller_id": None,
             "music_on_hold": None,
             "language": None,
             "timezone": None,
             "preprocess_subroutine": None,
             "password": None,
             "description": None}


class TestUserResource(s.GetScenarios, s.CreateScenarios, s.EditScenarios, s.DeleteScenarios):

    url = "/users"
    resource = "User"
    required = REQUIRED
    bogus_fields = BOGUS

    def create_resource(self):
        user = generate_user()
        return user['id']

    def test_invalid_mobile_phone_number(self):
        response = confd.users.post(firstname='fîrstname',
                                    mobile_phone_number='ai67cba74cba6kw4acwbc6w7')
        error = e.wrong_type(field='mobile_phone_number',
                             type='numeric phone number')
        response.assert_match(400, error)


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
@fixtures.device()
def test_updating_user_when_associated_to_user_and_line(user, line, extension, device):
    with a.user_line(user, line), \
            a.line_extension(line, extension), \
            a.line_device(line, device):

        response = confd.users(user['id']).put(firstname='fôobar')
        response.assert_ok()


def test_create_user_with_all_parameters_null():
    response = confd.users.post(**NULL_USER)
    assert_that(response.item, has_entries(NULL_USER))


@fixtures.user()
def test_update_user_with_all_parameters_null(user):
    response = confd.users(user['id']).put(**NULL_USER)
    response.assert_ok()

    response = confd.users(user['id']).get()
    assert_that(response.item, has_entries(**NULL_USER))


def test_create_user_generates_appropriate_caller_id():
    expected_caller_id = '"Jôhn"'
    response = confd.users.post(firstname='Jôhn')
    assert_that(response.item, has_entry('caller_id', expected_caller_id))

    expected_caller_id = '"Jôhn Doe"'
    response = confd.users.post(firstname='Jôhn', lastname='Doe')
    assert_that(response.item['caller_id'], equal_to(expected_caller_id))


@fixtures.user(firstname=u'Éric')
def test_that_the_directory_view_works_with_unicode_characters(user):
    response = confd.users.get(view='directory', q=u'éric')
    response.assert_ok()

    assert_that(response.items[0]['id'], equal_to(user['id']))


@fixtures.user(firstname="Snôm", lastname="Whîte")
@fixtures.user()
@fixtures.user()
def test_that_get_works_with_a_uuid(user_1, user_2_, user_3):
    result = confd.users(user_1['uuid']).get()

    assert_that(result.item, has_entries(firstname='Snôm', lastname='Whîte'))


@fixtures.user()
def test_that_users_can_be_deleted_by_uuid(user):
    response = confd.users(user['uuid']).delete()
    response.assert_ok()

    response = confd.users(user['uuid']).get()
    response.assert_status(404)


@fixtures.user()
def test_that_users_can_be_edited_by_uuid(user):
    response = confd.users(user['uuid']).put({'firstname': 'Fôo',
                                              'lastname': 'Bâr'})
    response.assert_ok()

    response = confd.users(user['uuid']).get()
    assert_that(response.item, has_entries(firstname='Fôo', lastname='Bâr'))


@fixtures.user(firstname="Lègacy", lastname="Usér")
def test_search_using_legacy_parameter(user):
    response = confd.users.get(q="lègacy usér")

    assert_that(response.items, has_item(has_entries(firstname="Lègacy", lastname="Usér")))


@fixtures.user(firstname="Léeroy",
               lastname="Jénkins",
               outgoing_caller_id='"Mystery Man" <5551234567>',
               username="leeroyjenkins",
               music_on_hold="leeroy_music_on_hold",
               mobile_phone_number="5552423232",
               userfield="leeroy jenkins userfield",
               description="Léeroy Jénkin's bio",
               preprocess_subroutine="leeroy_preprocess")
def test_search_on_user_view(user):
    url = confd.users
    searches = {
        'firstname': 'léeroy',
        'lastname': 'jénkins',
        'music_on_hold': 'leeroy_music',
        'outgoing_caller_id': '5551234567',
        'mobile_phone_number': '2423232',
        'userfield': 'jenkins userfield',
        'description': "jenkin's bio",
        'preprocess_subroutine': 'roy_preprocess',
    }

    for field, term in searches.items():
        yield check_search, url, user, field, term


@fixtures.user(firstname="Môustapha",
               lastname="Bângoura",
               mobile_phone_number="5559284759",
               userfield="Moustapha userfield",
               description="Moustapha the greatest dancer")
def test_search_on_directory_view(user):
    url = confd.users(view='directory')

    searches = {
        'firstname': 'môustapha',
        'lastname': 'bângoura',
        'mobile_phone_number': '928475',
        'userfield': 'moustapha userfield',
        'description': "greatest dancer",
    }

    for field, term in searches.items():
        yield check_search, url, user, field, term


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_search_on_users_extension(user, line, extension):
    with a.user_line(user, line), a.line_extension(line, extension):
        response = confd.users.get(search=extension['exten'], view='directory')
        assert_that(response.items, has_item(has_entry('exten', extension['exten'])))


def check_search(url, user, field, term):
    expected = has_item(has_entry(field, user[field]))
    response = url.get(search=term)
    assert_that(response.items, expected)
