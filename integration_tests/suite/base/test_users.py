# -*- coding: utf-8 -*-

# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
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
from test_api import config

from hamcrest import assert_that, equal_to, has_entries, has_entry, has_item, is_not, contains, none, empty


FULL_USER = {"firstname": "Jôhn",
             "lastname": "Smêth",
             "username": "jsmeth",
             "email": "jsmeth@smeth.com",
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
             "dtmf_hangup_enabled": True,
             "call_record_enabled": True,
             "online_call_record_enabled": True,
             "call_permission_password": '1234',
             "enabled": False,
             "ring_seconds": 60,
             "simultaneous_calls": 10}


NULL_USER = {"firstname": "Jôhn",
             "lastname": None,
             "username": None,
             "email": None,
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
             "dtmf_hangup_enabled": False,
             "call_record_enabled": False,
             "online_call_record_enabled": False,
             "call_permission_password": None,
             "enabled": True,
             "ring_seconds": 30,
             "simultaneous_calls": 5}


def test_search_errors():
    url = confd.users.get
    for check in s.search_error_checks(url):
        yield check


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
    yield s.check_bogus_field_returns_error, url, 'firstname', None
    yield s.check_bogus_field_returns_error, url, 'firstname', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'firstname', {}
    yield s.check_bogus_field_returns_error, url, 'firstname', []
    yield s.check_bogus_field_returns_error, url, 'lastname', 123
    yield s.check_bogus_field_returns_error, url, 'lastname', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'lastname', {}
    yield s.check_bogus_field_returns_error, url, 'lastname', []
    yield s.check_bogus_field_returns_error, url, 'email', s.random_string(255)
    yield s.check_bogus_field_returns_error, url, 'email', 123
    yield s.check_bogus_field_returns_error, url, 'email', {}
    yield s.check_bogus_field_returns_error, url, 'email', []
    yield s.check_bogus_field_returns_error, url, 'timezone', 123
    yield s.check_bogus_field_returns_error, url, 'timezone', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'timezone', {}
    yield s.check_bogus_field_returns_error, url, 'timezone', []
    yield s.check_bogus_field_returns_error, url, 'language', 123
    yield s.check_bogus_field_returns_error, url, 'language', 'klingon'
    yield s.check_bogus_field_returns_error, url, 'language', {}
    yield s.check_bogus_field_returns_error, url, 'language', []
    yield s.check_bogus_field_returns_error, url, 'description', 123
    yield s.check_bogus_field_returns_error, url, 'description', {}
    yield s.check_bogus_field_returns_error, url, 'description', []
    yield s.check_bogus_field_returns_error, url, 'caller_id', 123
    yield s.check_bogus_field_returns_error, url, 'caller_id', 'invalid_regex'
    yield s.check_bogus_field_returns_error, url, 'caller_id', s.random_string(161)
    yield s.check_bogus_field_returns_error, url, 'caller_id', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id', []
    yield s.check_bogus_field_returns_error, url, 'outgoing_caller_id', 123
    yield s.check_bogus_field_returns_error, url, 'outgoing_caller_id', s.random_string(81)
    yield s.check_bogus_field_returns_error, url, 'outgoing_caller_id', {}
    yield s.check_bogus_field_returns_error, url, 'outgoing_caller_id', []
    yield s.check_bogus_field_returns_error, url, 'mobile_phone_number', 123
    yield s.check_bogus_field_returns_error, url, 'mobile_phone_number', 'invalid_regex'
    yield s.check_bogus_field_returns_error, url, 'mobile_phone_number', '123abcd'
    yield s.check_bogus_field_returns_error, url, 'mobile_phone_number', s.random_string(81)
    yield s.check_bogus_field_returns_error, url, 'mobile_phone_number', {}
    yield s.check_bogus_field_returns_error, url, 'mobile_phone_number', []
    yield s.check_bogus_field_returns_error, url, 'username', 123
    yield s.check_bogus_field_returns_error, url, 'username', 'invalid_régex'
    yield s.check_bogus_field_returns_error, url, 'username', s.random_string(1)
    yield s.check_bogus_field_returns_error, url, 'username', s.random_string(255)
    yield s.check_bogus_field_returns_error, url, 'username', {}
    yield s.check_bogus_field_returns_error, url, 'username', []
    yield s.check_bogus_field_returns_error, url, 'password', 123
    yield s.check_bogus_field_returns_error, url, 'password', 'invalid_régex'
    yield s.check_bogus_field_returns_error, url, 'password', s.random_string(3)
    yield s.check_bogus_field_returns_error, url, 'password', s.random_string(65)
    yield s.check_bogus_field_returns_error, url, 'password', {}
    yield s.check_bogus_field_returns_error, url, 'password', []
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', 123
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', {}
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', []
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', 123
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', s.random_string(40)
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', {}
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', []
    yield s.check_bogus_field_returns_error, url, 'userfield', 123
    yield s.check_bogus_field_returns_error, url, 'userfield', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'userfield', {}
    yield s.check_bogus_field_returns_error, url, 'userfield', []
    yield s.check_bogus_field_returns_error, url, 'caller_id', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'caller_id', 1234
    yield s.check_bogus_field_returns_error, url, 'caller_id', s.random_string(161)
    yield s.check_bogus_field_returns_error, url, 'caller_id', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id', []
    yield s.check_bogus_field_returns_error, url, 'call_transfer_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'call_transfer_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'call_transfer_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'call_transfer_enabled', []
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_enabled', []
    yield s.check_bogus_field_returns_error, url, 'call_record_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'call_record_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'call_record_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'call_record_enabled', []
    yield s.check_bogus_field_returns_error, url, 'online_call_record_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'online_call_record_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'online_call_record_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'online_call_record_enabled', []
    yield s.check_bogus_field_returns_error, url, 'supervision_enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'supervision_enabled', 123
    yield s.check_bogus_field_returns_error, url, 'supervision_enabled', {}
    yield s.check_bogus_field_returns_error, url, 'supervision_enabled', []
    yield s.check_bogus_field_returns_error, url, 'simultaneous_calls', 'sixty'
    yield s.check_bogus_field_returns_error, url, 'simultaneous_calls', -1
    yield s.check_bogus_field_returns_error, url, 'simultaneous_calls', 21
    yield s.check_bogus_field_returns_error, url, 'simultaneous_calls', {}
    yield s.check_bogus_field_returns_error, url, 'simultaneous_calls', []
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', 'ten'
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', -1
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', 61
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', {}
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', []
    yield s.check_bogus_field_returns_error, url, 'call_permission_password', 1234
    yield s.check_bogus_field_returns_error, url, 'call_permission_password', 'invalid_char'
    yield s.check_bogus_field_returns_error, url, 'call_permission_password', {}
    yield s.check_bogus_field_returns_error, url, 'call_permission_password', []
    yield s.check_bogus_field_returns_error, url, 'call_permission_password', s.random_string(17)
    yield s.check_bogus_field_returns_error, url, 'enabled', 'yeah'
    yield s.check_bogus_field_returns_error, url, 'enabled', 123
    yield s.check_bogus_field_returns_error, url, 'enabled', {}
    yield s.check_bogus_field_returns_error, url, 'enabled', []


def put_error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'caller_id', None
    yield s.check_bogus_field_returns_error, url, 'call_transfer_enabled', None
    yield s.check_bogus_field_returns_error, url, 'dtmf_hangup_enabled', None
    yield s.check_bogus_field_returns_error, url, 'call_record_enabled', None
    yield s.check_bogus_field_returns_error, url, 'online_call_record_enabled', None
    yield s.check_bogus_field_returns_error, url, 'supervision_enabled', None
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', None
    yield s.check_bogus_field_returns_error, url, 'simultaneous_calls', None
    yield s.check_bogus_field_returns_error, url, 'ring_seconds', None
    yield s.check_bogus_field_returns_error, url, 'enabled', None


@fixtures.user()
def test_put_errors(user):
    user_put = confd.users(user['id']).put

    for check in error_checks(user_put):
        yield check
    for check in put_error_checks(user_put):
        yield check


@fixtures.user(firstname='user1', username='unique_username', email='unique@email')
@fixtures.user()
def test_unique_errors(user1, user2):
    url = confd.users(user2['id']).put
    for check in unique_error_checks(url, user1):
        yield check

    required_body = {'firstname': 'user2'}
    url = confd.users.post
    for check in unique_error_checks(url, user1, required_body):
        yield check


def unique_error_checks(url, existing_resource, required_body=None):
    yield s.check_bogus_field_returns_error, url, 'username', existing_resource['username'], required_body
    yield s.check_bogus_field_returns_error, url, 'email', existing_resource['email'], required_body


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


@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_summary_view_on_sip_endpoint(user, line, sip, extension):
    expected = has_entries(id=user['id'],
                           uuid=user['uuid'],
                           firstname=user['firstname'],
                           lastname=user['lastname'],
                           email=user['email'],
                           provisioning_code=line['provisioning_code'],
                           extension=extension['exten'],
                           context=extension['context'],
                           entity=config.ENTITY_NAME,
                           enabled=True,
                           protocol='sip')

    with a.line_endpoint_sip(line, sip), a.line_extension(line, extension), \
            a.user_line(user, line):

        response = confd.users.get(view='summary', id=user['id'])
        assert_that(response.items, contains(expected))


@fixtures.user()
@fixtures.line()
@fixtures.sccp()
@fixtures.extension()
def test_summary_view_on_sccp_endpoint(user, line, sccp, extension):
    expected = has_entries(id=user['id'],
                           uuid=user['uuid'],
                           firstname=user['firstname'],
                           lastname=user['lastname'],
                           email=user['email'],
                           provisioning_code=none(),
                           extension=extension['exten'],
                           context=extension['context'],
                           entity=config.ENTITY_NAME,
                           enabled=True,
                           protocol='sccp')

    with a.line_endpoint_sccp(line, sccp), a.line_extension(line, extension), \
            a.user_line(user, line):

        response = confd.users.get(view='summary', id=user['id'])
        assert_that(response.items, contains(expected))


@fixtures.user()
@fixtures.line()
@fixtures.custom()
@fixtures.extension()
def test_summary_view_on_custom_endpoint(user, line, custom, extension):
    expected = has_entries(id=user['id'],
                           uuid=user['uuid'],
                           firstname=user['firstname'],
                           lastname=user['lastname'],
                           email=user['email'],
                           provisioning_code=none(),
                           extension=extension['exten'],
                           context=extension['context'],
                           entity=config.ENTITY_NAME,
                           enabled=True,
                           protocol='custom')

    with a.line_endpoint_custom(line, custom), a.line_extension(line, extension), \
            a.user_line(user, line):

        response = confd.users.get(view='summary', id=user['id'])
        assert_that(response.items, contains(expected))


@fixtures.user()
def test_summary_view_on_user_without_line(user):
    expected = has_entries(id=user['id'],
                           uuid=user['uuid'],
                           firstname=user['firstname'],
                           lastname=user['lastname'],
                           email=user['email'],
                           provisioning_code=none(),
                           extension=none(),
                           context=none(),
                           entity=config.ENTITY_NAME,
                           enabled=True,
                           protocol=none())

    response = confd.users.get(view='summary', id=user['id'])
    assert_that(response.items, contains(expected))


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
               email="jenkins@leeroy.com",
               outgoing_caller_id='"Mystery Man" <5551234567>',
               username="leeroyjenkins",
               music_on_hold="leeroy_music_on_hold",
               mobile_phone_number="5552423232",
               userfield="leeroy jenkins userfield",
               description="Léeroy Jénkin's bio",
               enabled=False,
               preprocess_subroutine="leeroy_preprocess")
def test_search_on_user_view(user):
    url = confd.users
    searches = {
        'firstname': 'léeroy',
        'lastname': 'jénkins',
        'email': 'jenkins@',
        'music_on_hold': 'leeroy_music',
        'outgoing_caller_id': '5551234567',
        'mobile_phone_number': '2423232',
        'userfield': 'jenkins userfield',
        'description': "jénkin's bio",
        'preprocess_subroutine': 'roy_preprocess',
    }

    for field, term in searches.items():
        yield check_search, url, field, term, user[field]


@fixtures.user(firstname="Môustapha",
               lastname="Bângoura",
               email="moustapha@bangoura.com",
               mobile_phone_number="+5559284759",
               userfield="Moustapha userfield",
               description="Moustapha the greatest dancer")
def test_search_on_directory_view(user):
    url = confd.users(view='directory')

    searches = {
        'firstname': 'môustapha',
        'lastname': 'bângoura',
        'email': 'moustapha@',
        'mobile_phone_number': '928475',
        'userfield': 'moustapha userfield',
        'description': "greatest dancer",
    }

    for field, term in searches.items():
        yield check_search, url, field, term, user[field]


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


@fixtures.user(firstname="Âboubacar",
               lastname="Manè",
               description="Âboubacar le grand danseur")
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_search_on_summary_view(user, line, sip, extension):
    url = confd.users(view='summary')

    with a.line_endpoint_sip(line, sip), a.user_line(user, line), a.line_extension(line, extension):
        yield check_search, url, 'firstname', 'âbou', user['firstname']
        yield check_search, url, 'lastname', 'man', user['lastname']
        yield check_search, url, 'provisioning_code', line['provisioning_code'], line['provisioning_code']
        yield check_search, url, 'extension', extension['exten'], extension['exten']


def check_search(url, field, term, value):
    expected = has_item(has_entry(field, value))
    response = url.get(search=term)
    assert_that(response.items, expected)


@fixtures.user(firstname="firstname1",
               lastname="lastname1",
               email="email1@example.com",
               mobile_phone_number="+5551",
               userfield="sort userfield1",
               description="description1")
@fixtures.user(firstname="firstname2",
               lastname="lastname2",
               email="email2@example.com",
               mobile_phone_number="+5552",
               userfield="sort userfield2",
               description="description2")
def test_sorting_offset_limit(user1, user2):
    url = confd.users.get
    yield s.check_sorting, url, user1, user2, 'firstname', 'firstname'
    yield s.check_sorting, url, user1, user2, 'lastname', 'lastname'
    yield s.check_sorting, url, user1, user2, 'email', 'email'
    yield s.check_sorting, url, user1, user2, 'mobile_phone_number', '+555'
    yield s.check_sorting, url, user1, user2, 'userfield', 'sort userfield'
    yield s.check_sorting, url, user1, user2, 'description', 'description'

    yield s.check_offset, url, user1, user2, 'firstname', 'firstname'
    yield s.check_offset_legacy, url, user1, user2, 'firstname', 'firstname'

    yield s.check_limit, url, user1, user2, 'firstname', 'firstname'


@fixtures.user(**FULL_USER)
def test_get_user(user):
    response = confd.users(user['id']).get()
    assert_that(response.item, has_entries(FULL_USER))
    assert_that(response.item, has_entries(
        agent=none(),
        incalls=empty(),
        lines=empty(),
        groups=empty(),
        forwards={'busy': {'destination': None, 'enabled': False},
                  'noanswer': {'destination': None, 'enabled': False},
                  'unconditional': {'destination': None, 'enabled': False}},
        services={'dnd': {'enabled': False},
                  'incallfilter': {'enabled': False}},
        voicemail=none(),
    ))


@fixtures.user(firstname="Snôm", lastname="Whîte")
@fixtures.user()
@fixtures.user()
def test_that_get_works_with_a_uuid(user_1, user_2_, user_3):
    result = confd.users(user_1['uuid']).get()

    assert_that(result.item, has_entries(firstname='Snôm', lastname='Whîte'))


@fixtures.user(firstname="Snôw", lastname="Whîte", username='snow.white+dwarves@disney.example.com')
def test_that_the_username_can_be_an_email(user):
    result = confd.users(user['id']).get()

    assert_that(result.item, has_entries(firstname='Snôw',
                                         lastname='Whîte',
                                         username='snow.white+dwarves@disney.example.com'))


def test_create_minimal_parameters():
    response = confd.users.post(firstname="Roger")

    response.assert_created('users')
    assert_that(response.item, has_entry("firstname", "Roger"))


def test_create_with_null_parameters_fills_default_values():
    response = confd.users.post(firstname="Charlie")
    response.assert_created('users')

    assert_that(response.item, has_entries(caller_id='"Charlie"',
                                           call_transfer_enabled=False,
                                           dtmf_hangup_enabled=False,
                                           call_record_enabled=False,
                                           online_call_record_enabled=False,
                                           supervision_enabled=True,
                                           ring_seconds=30,
                                           simultaneous_calls=5))


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


@fixtures.user(firstname="Léeroy",
               lastname="Jénkins",
               email="leeroy@jenkins.com",
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
