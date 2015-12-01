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
from test_api import associations as a
from test_api import confd
from test_api import fixtures

from hamcrest import assert_that, equal_to, has_entries, has_entry, has_item, is_not


FULL_USER = {"firstname": "Jôhn",
             "lastname": "Smêth",
             "username": "jsmeth",
             "mobile_phone_number": "+4185551234*2",
             "userfield": "userfield",
             "caller_id": '"Jôhnny Smith" <4185551234>',
             "outgoing_caller_id": '"Johnny" <123>',
             "music_on_hold": "default",
             "language": "fr_FR",
             "timezone": "America/Montreal",
             "preprocess_subroutine": "preprocess_subroutine",
             "password": "password",
             "description": "John's description",
             "supervision_enabled": False,
             "call_transfer_enabled": False,
             "ring_seconds": 60,
             "simultaneous_calls": 10}


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
             "description": None,
             "supervision_enabled": True,
             "call_transfer_enabled": True,
             "ring_seconds": 30,
             "simultaneous_calls": 5}


def test_get_errors():
    fake_get = confd.users(999999).get
    yield s.check_resource_not_found, fake_get, 'User'


def test_post_errors():
    empty_post = confd.users.post
    user_post = confd.users(firstname="Jôhn").post

    yield s.check_missing_required_field_returns_error, empty_post, 'firstname'
    for check in error_checks(user_post):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'firstname', 123
    yield s.check_bogus_field_returns_error, url, 'lastname', 123
    yield s.check_bogus_field_returns_error, url, 'timezone', 123
    yield s.check_bogus_field_returns_error, url, 'language', 123
    yield s.check_bogus_field_returns_error, url, 'description', 123
    yield s.check_bogus_field_returns_error, url, 'caller_id', 123
    yield s.check_bogus_field_returns_error, url, 'outgoing_caller_id', 123
    yield s.check_bogus_field_returns_error, url, 'mobile_phone_number', 123
    yield s.check_bogus_field_returns_error, url, 'username', 123
    yield s.check_bogus_field_returns_error, url, 'password', 123
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', 123
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', 123
    yield s.check_bogus_field_returns_error, url, 'userfield', 123
    yield s.check_bogus_field_returns_error, url, 'caller_id', 'callerid'
    yield s.check_bogus_field_returns_error, url, 'mobile_phone_number', '123abcd'
    yield s.check_bogus_field_returns_error, url, 'call_transfer_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'supervision_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', 'ten'
    yield s.check_bogus_field_returns_error, url, 'simultaneous_calls', 'sixty'


@fixtures.user()
def test_put_errors(user):
    user_put = confd.users(user['id']).put

    for check in error_checks(user_put):
        yield check


@fixtures.user()
def test_delete_errors(user):
    user_url = confd.users(user['id'])
    user_url.delete()
    yield s.check_resource_not_found, user_url.get, 'User'


@fixtures.user(firstname=u'ÉricDir')
def test_that_the_directory_view_works_with_unicode_characters(user):
    response = confd.users.get(view='directory', search=u'éricdir')
    response.assert_ok()

    assert_that(response.items[0]['id'], equal_to(user['id']))


@fixtures.user(firstname="Lègacy", lastname="Usér")
@fixtures.user(firstname="Hîde", lastname="Mé")
def test_search_using_legacy_parameter(user1, user2):
    expected_found = has_item(has_entries(firstname="Lègacy", lastname="Usér"))
    expected_hidden = has_item(has_entries(firstname="Hîde", lastname="Mé"))

    response = confd.users.get(q="lègacy usér")

    assert_that(response.items, expected_found)
    assert_that(response.items, is_not(expected_hidden))


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
               mobile_phone_number="+5559284759",
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


@fixtures.user(firstname='Alicé')
@fixtures.line_sip()
@fixtures.extension()
def test_search_on_users_with_context_filter(user, line, extension):
    with a.user_line(user, line), a.line_extension(line, extension):
        response = confd.users.get(search='ali', view='directory', context='default')
        assert_that(response.total, equal_to(1))
        assert_that(response.items, has_item(has_entry('exten', extension['exten'])))

        response = confd.users.get(search='ali', view='directory', context='other')
        assert_that(response.total, equal_to(0))


def check_search(url, user, field, term):
    expected = has_item(has_entry(field, user[field]))
    response = url.get(search=term)
    assert_that(response.items, expected)


@fixtures.user(**FULL_USER)
def test_get_user(user):
    response = confd.users(user['id']).get()
    assert_that(response.item, has_entries(FULL_USER))


@fixtures.user(firstname="Snôm", lastname="Whîte")
@fixtures.user()
@fixtures.user()
def test_that_get_works_with_a_uuid(user_1, user_2_, user_3):
    result = confd.users(user_1['uuid']).get()

    assert_that(result.item, has_entries(firstname='Snôm', lastname='Whîte'))


def test_create_minimal_parameters():
    response = confd.users.post(firstname="Roger")

    response.assert_created('users')
    assert_that(response.item, has_entry("firstname", "Roger"))


def test_create_user_with_all_parameters():
    response = confd.users.post(**FULL_USER)

    response.assert_created('users')
    assert_that(response.item, has_entries(FULL_USER))


def test_create_user_with_all_parameters_null():
    response = confd.users.post(**NULL_USER)
    assert_that(response.item, has_entries(NULL_USER))


def test_create_user_generates_appropriate_caller_id():
    expected_caller_id = '"Jôhn"'
    response = confd.users.post(firstname='Jôhn')
    assert_that(response.item, has_entry('caller_id', expected_caller_id))

    expected_caller_id = '"Jôhn Doe"'
    response = confd.users.post(firstname='Jôhn', lastname='Doe')
    assert_that(response.item['caller_id'], equal_to(expected_caller_id))


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
@fixtures.device()
def test_updating_user_when_associated_to_user_and_line(user, line, extension, device):
    with a.user_line(user, line), \
            a.line_extension(line, extension), \
            a.line_device(line, device):

        response = confd.users(user['id']).put(firstname='fôobar')
        response.assert_updated()


@fixtures.user(firstname="Léeroy",
               lastname="Jénkins",
               outgoing_caller_id='"Mystery Man" <5551234567>',
               username="leeroyjenkins",
               music_on_hold="leeroy_music_on_hold",
               mobile_phone_number="5552423232",
               userfield="leeroy jenkins userfield",
               description="Léeroy Jénkin's bio",
               preprocess_subroutine="leeroy_preprocess")
def test_update_user_with_all_parameters(user):
    user_url = confd.users(user['id'])

    response = user_url.put(**FULL_USER)
    response.assert_updated()

    response = user_url.get()
    assert_that(response.item, has_entries(FULL_USER))


@fixtures.user()
def test_update_user_with_all_parameters_null(user):
    response = confd.users(user['id']).put(**NULL_USER)
    response.assert_updated()

    response = confd.users(user['id']).get()
    assert_that(response.item, has_entries(**NULL_USER))


@fixtures.user()
def test_that_users_can_be_edited_by_uuid(user):
    response = confd.users(user['uuid']).put({'firstname': 'Fôo',
                                              'lastname': 'Bâr'})
    response.assert_updated()

    response = confd.users(user['uuid']).get()
    assert_that(response.item, has_entries(firstname='Fôo', lastname='Bâr'))


@fixtures.user()
def test_delete(user):
    response = confd.users(user['id']).delete()
    response.assert_deleted()


@fixtures.user()
def test_that_users_can_be_deleted_by_uuid(user):
    response = confd.users(user['uuid']).delete()
    response.assert_deleted()

    response = confd.users(user['uuid']).get()
    response.assert_status(404)
