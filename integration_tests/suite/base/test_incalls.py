# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from test_api import associations as a
from test_api import confd
from test_api import errors as e
from test_api import fixtures
from test_api import scenarios as s
from test_api.config import INCALL_CONTEXT

from hamcrest import (assert_that,
                      contains,
                      empty,
                      has_entries,
                      has_entry,
                      has_item,
                      is_not,
                      not_)


invalid_destinations = [
    None,
    1234,
    'string',
    {'type': 'invalid'},

    {'type': 'application'},
    {'type': 'application', 'missing_required_field': 'disa'},
    {'type': 'application', 'application': 'invalid'},

    {'type': 'application', 'application': 'callback_disa', 'context': True},
    {'type': 'application', 'application': 'callback_disa', 'context': None},
    {'type': 'application', 'application': 'callback_disa', 'context': 'invalid_char_@'},
    {'type': 'application', 'application': 'callback_disa', 'context': s.random_string(40)},
    {'type': 'application', 'application': 'callback_disa', 'context': 'default', 'pin': 'invalid'},
    {'type': 'application', 'application': 'callback_disa', 'context': 'default', 'pin': True},
    {'type': 'application', 'application': 'callback_disa', 'context': 'default', 'pin': 1234},
    {'type': 'application', 'application': 'callback_disa', 'context': 'default', 'pin': '#123'},
    {'type': 'application', 'application': 'callback_disa', 'context': 'default', 'pin': s.random_string(41)},

    {'type': 'application', 'application': 'directory', 'context': True},
    {'type': 'application', 'application': 'directory', 'context': None},
    {'type': 'application', 'application': 'directory', 'context': 'invalid_char_@'},
    {'type': 'application', 'application': 'directory', 'context': s.random_string(40)},

    {'type': 'application', 'application': 'disa', 'context': True},
    {'type': 'application', 'application': 'disa', 'context': None},
    {'type': 'application', 'application': 'disa', 'context': 'invalid_char_@'},
    {'type': 'application', 'application': 'disa', 'context': s.random_string(40)},
    {'type': 'application', 'application': 'disa', 'context': 'default', 'pin': 'invalid'},
    {'type': 'application', 'application': 'disa', 'context': 'default', 'pin': True},
    {'type': 'application', 'application': 'disa', 'context': 'default', 'pin': 1234},
    {'type': 'application', 'application': 'disa', 'context': 'default', 'pin': '#123'},
    {'type': 'application', 'application': 'disa', 'context': 'default', 'pin': s.random_string(41)},

    {'type': 'application', 'application': 'fax_to_mail', 'email': 'invalid'},
    {'type': 'application', 'application': 'fax_to_mail', 'email': 1234},
    {'type': 'application', 'application': 'fax_to_mail', 'email': True},
    {'type': 'application', 'application': 'fax_to_mail', 'email': None},
    {'type': 'application', 'application': 'fax_to_mail', 'email': s.random_string(81)},

    {'type': 'application', 'application': 'voicemail', 'context': True},
    {'type': 'application', 'application': 'voicemail', 'context': None},
    {'type': 'application', 'application': 'voicemail', 'context': 'invalid_char_@'},
    {'type': 'application', 'application': 'voicemail', 'context': s.random_string(40)},

    {'type': 'conference'},
    {'type': 'conference', 'missing_required_field': 123},
    {'type': 'conference', 'conference_id': 'string'},
    {'type': 'conference', 'conference_id': None},

    {'type': 'custom'},
    {'type': 'custom', 'missing_required_field': '123'},
    {'type': 'custom', 'command': 1234},
    {'type': 'custom', 'command': True},
    {'type': 'custom', 'command': None},
    {'type': 'custom', 'command': 'invalid'},
    {'type': 'custom', 'command': 'system(not_authorized)'},
    {'type': 'custom', 'command': 'trysystem(not_authorized)'},
    {'type': 'custom', 'command': s.random_string(256)},

    {'type': 'extension'},
    {'type': 'extension', 'missing_required_field': '123'},
    {'type': 'extension', 'context': True},
    {'type': 'extension', 'context': None},
    {'type': 'extension', 'context': 'invalid_char_@'},
    {'type': 'extension', 'context': s.random_string(40)},
    {'type': 'extension', 'context': 'default', 'exten': 1234},
    {'type': 'extension', 'context': 'default', 'exten': True},
    {'type': 'extension', 'context': 'default', 'exten': None},
    {'type': 'extension', 'context': 'default', 'exten': '*1234#??'},

    {'type': 'group'},
    {'type': 'group', 'missing_required_field': 123},
    {'type': 'group', 'group_id': 'string'},
    {'type': 'group', 'group_id': None},

    {'type': 'hangup', 'cause': 'invalid'},

    {'type': 'hangup', 'cause': 'busy', 'timeout': 'invalid'},

    {'type': 'hangup', 'cause': 'congestion', 'timeout': 'invalid'},

    {'type': 'outcall'},
    {'type': 'outcall', 'missing_required_field': 123},
    {'type': 'outcall', 'outcall_id': 'string'},
    {'type': 'outcall', 'outcall_id': None},

    {'type': 'queue'},
    {'type': 'queue', 'missing_required_field': 123},
    {'type': 'queue', 'queue_id': 'string'},
    {'type': 'queue', 'queue_id': None},

    {'type': 'sound'},
    {'type': 'sound', 'missing_required_field': 'string'},
    {'type': 'sound', 'filename': 1234},
    {'type': 'sound', 'filename': None},
    {'type': 'sound', 'filename': s.random_string(256)},
    {'type': 'sound', 'filename': 'daddy-cool', 'skip': None},
    {'type': 'sound', 'filename': 'daddy-cool', 'skip': 123},
    {'type': 'sound', 'filename': 'daddy-cool', 'skip': 'invalid'},
    {'type': 'sound', 'filename': 'daddy-cool', 'skip': []},
    {'type': 'sound', 'filename': 'daddy-cool', 'skip': {}},
    {'type': 'sound', 'filename': 'daddy-cool', 'no_answer': None},
    {'type': 'sound', 'filename': 'daddy-cool', 'no_answer': 123},
    {'type': 'sound', 'filename': 'daddy-cool', 'no_answer': 'invalid'},
    {'type': 'sound', 'filename': 'daddy-cool', 'no_answer': []},
    {'type': 'sound', 'filename': 'daddy-cool', 'no_answer': {}},

    {'type': 'user'},
    {'type': 'user', 'missing_required_field': 123},
    {'type': 'user', 'user_id': 'string'},
    {'type': 'user', 'user_id': None},

    {'type': 'voicemail'},
    {'type': 'voicemail', 'missing_required_field': 123},
    {'type': 'voicemail', 'voicemail_id': 'string'},
    {'type': 'voicemail', 'voicemail_id': None},
    {'type': 'voicemail', 'voicemail_id': 1, 'skip_instructions': None},
    {'type': 'voicemail', 'voicemail_id': 1, 'skip_instructions': 'string'},
    {'type': 'voicemail', 'voicemail_id': 1, 'greeting': True},
    {'type': 'voicemail', 'voicemail_id': 1, 'greeting': 'invalid'},
]


def test_get_errors():
    fake_incall = confd.incalls(999999).get
    yield s.check_resource_not_found, fake_incall, 'Incall'


def test_delete_errors():
    fake_incall = confd.incalls(999999).delete
    yield s.check_resource_not_found, fake_incall, 'Incall'


def test_post_errors():
    url = confd.incalls.post
    for check in error_checks(url):
        yield check


@fixtures.incall()
def test_put_errors(incall):
    url = confd.incalls(incall['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', 123
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', s.random_string(40)
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', []
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', True
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', 1234
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', []
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', 1234
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', True
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', s.random_string(81)
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', []
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', {}
    yield s.check_bogus_field_returns_error, url, 'description', 1234
    yield s.check_bogus_field_returns_error, url, 'description', []
    yield s.check_bogus_field_returns_error, url, 'destination', {}

    for destination in invalid_destinations:
        yield s.check_bogus_field_returns_error, url, 'destination', destination


@fixtures.incall(description='search')
@fixtures.incall(description='hidden')
def test_search(incall, hidden):
    url = confd.incalls
    searches = {'description': 'search'}

    for field, term in searches.items():
        yield check_search, url, incall, hidden, field, term


def check_search(url, incall, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, incall[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: incall[field]})

    expected = has_item(has_entry('id', incall['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.incall(description='sort1')
@fixtures.incall(description='sort2')
def test_sorting(incall1, incall2):
    yield check_sorting, incall1, incall2, 'description', 'sort'


def check_sorting(incall1, incall2, field, search):
    response = confd.incalls.get(search=search, order=field, direction='asc')
    assert_that(response.items, contains(has_entries(id=incall1['id']),
                                         has_entries(id=incall2['id'])))

    response = confd.incalls.get(search=search, order=field, direction='desc')
    assert_that(response.items, contains(has_entries(id=incall2['id']),
                                         has_entries(id=incall1['id'])))


@fixtures.incall()
def test_get(incall):
    response = confd.incalls(incall['id']).get()
    assert_that(response.item, has_entries(id=incall['id'],
                                           preprocess_subroutine=incall['preprocess_subroutine'],
                                           description=incall['description'],
                                           caller_id_mode=incall['caller_id_mode'],
                                           caller_id_name=incall['caller_id_name'],
                                           destination=incall['destination']))


@fixtures.incall()
@fixtures.extension(context=INCALL_CONTEXT)
def test_get_relations(incall, extension):
    expected = has_entries(
        extensions=contains(has_entries(id=extension['id'],
                                        exten=extension['exten'],
                                        context=extension['context']))
    )

    with a.incall_extension(incall, extension):
        response = confd.incalls(incall['id']).get()
        assert_that(response.item, expected)


def test_create_minimal_parameters():
    response = confd.incalls.post(destination={'type': 'none'})
    response.assert_created('incalls')

    assert_that(response.item, has_entries(id=not_(empty())))


def test_create_all_parameters():
    response = confd.incalls.post(preprocess_subroutine='default',
                                  description='description',
                                  caller_id_mode='prepend',
                                  caller_id_name='name_',
                                  destination={'type': 'none'})
    response.assert_created('incalls')

    assert_that(response.item, has_entries(preprocess_subroutine='default',
                                           description='description',
                                           caller_id_mode='prepend',
                                           caller_id_name='name_',
                                           destination={'type': 'none'}))


@fixtures.incall(destination={'type': 'hangup'})
def test_edit_minimal_parameters(incall):
    parameters = {'destination': {'type': 'none'}}

    response = confd.incalls(incall['id']).put(**parameters)
    response.assert_updated()


@fixtures.incall()
def test_edit_all_parameters(incall):
    parameters = {'destination': {'type': 'none'},
                  'preprocess_subroutine': 'default',
                  'caller_id_mode': 'append',
                  'caller_id_name': '_name',
                  'description': 'description'}

    response = confd.incalls(incall['id']).put(**parameters)
    response.assert_updated()

    response = confd.incalls(incall['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.incall()
@fixtures.conference()
@fixtures.group()
@fixtures.outcall()
@fixtures.queue()
@fixtures.user()
@fixtures.voicemail()
def test_valid_destinations(incall, conference, group, outcall, queue, user, voicemail):
    valid_destinations = [
        {'type': 'application', 'application': 'callback_disa',
         'context': 'name'},
        {'type': 'application', 'application': 'callback_disa',
         'pin': '1234', 'context': 'name'},
        {'type': 'application', 'application': 'callback_disa',
         'pin': None, 'context': 'name'},
        {'type': 'application', 'application': 'directory',
         'context': 'name'},
        {'type': 'application', 'application': 'disa',
         'context': 'name'},
        {'type': 'application', 'application': 'disa',
         'pin': '1234', 'context': 'name'},
        {'type': 'application', 'application': 'disa',
         'pin': None, 'context': 'name'},
        {'type': 'application', 'application': 'fax_to_mail',
         'email': 'toto@example.com'},
        {'type': 'application', 'application': 'voicemail',
         'context': 'name'},
        {'type': 'conference', 'conference_id': conference['id']},
        {'type': 'custom', 'command': 'Playback(toto)'},
        {'type': 'extension', 'exten': '1001', 'context': 'name'},
        {'type': 'group', 'group_id': group['id']},
        {'type': 'group', 'group_id': group['id'], 'ring_time': 1.5},
        {'type': 'group', 'group_id': group['id'], 'ring_time': None},
        {'type': 'hangup', 'cause': 'normal'},
        {'type': 'hangup', 'cause': 'busy'},
        {'type': 'hangup', 'cause': 'busy', 'timeout': 1.6},
        {'type': 'hangup', 'cause': 'busy', 'timeout': None},
        {'type': 'hangup', 'cause': 'congestion'},
        {'type': 'hangup', 'cause': 'congestion', 'timeout': 0.6},
        {'type': 'hangup', 'cause': 'congestion', 'timeout': None},
        {'type': 'none'},
        {'type': 'outcall', 'outcall_id': outcall['id'], 'exten': '1234567890'},
        {'type': 'queue', 'queue_id': queue['id']},
        {'type': 'queue', 'queue_id': queue['id'], 'ring_time': 0.9},
        {'type': 'queue', 'queue_id': queue['id'], 'ring_time': None},
        {'type': 'sound', 'filename': 'filename_without_extension'},
        {'type': 'sound', 'filename': 'filename_without_extension',
         'skip': True},
        {'type': 'sound', 'filename': 'filename_without_extension',
         'no_answer': True},
        {'type': 'sound', 'filename': 'filename_without_extension',
         'skip': True, 'no_answer': True},
        {'type': 'sound', 'filename': 'filename_without_extension',
         'skip': False, 'no_answer': False},
        {'type': 'user', 'user_id': user['id']},
        {'type': 'user', 'user_id': user['id'], 'ring_time': 2},
        {'type': 'user', 'user_id': user['id'], 'ring_time': None},
        {'type': 'voicemail', 'voicemail_id': voicemail['id']},
        {'type': 'voicemail', 'voicemail_id': voicemail['id'],
         'skip_instructions': True},
        {'type': 'voicemail', 'voicemail_id': voicemail['id'],
         'greeting': None},
        {'type': 'voicemail', 'voicemail_id': voicemail['id'],
         'skip_instructions': True, 'greeting': None},
        {'type': 'voicemail', 'voicemail_id': voicemail['id'],
         'skip_instructions': True, 'greeting': 'busy'},
        {'type': 'voicemail', 'voicemail_id': voicemail['id'],
         'skip_instructions': False, 'greeting': 'unavailable'},
    ]

    for destination in valid_destinations:
        yield create_incall_with_destination, destination
        yield update_incall_with_destination, incall['id'], destination


def create_incall_with_destination(destination):
    response = confd.incalls.post(destination=destination)
    response.assert_created('incalls')
    assert_that(response.item, has_entries(destination=has_entries(**destination)))


def update_incall_with_destination(incall_id, destination):
    response = confd.incalls(incall_id).put(destination=destination)
    response.assert_updated()
    response = confd.incalls(incall_id).get()
    assert_that(response.item, has_entries(destination=has_entries(**destination)))


@fixtures.incall()
def test_delete(incall):
    response = confd.incalls(incall['id']).delete()
    response.assert_deleted()
    response = confd.incalls(incall['id']).get()
    response.assert_match(404, e.not_found(resource='Incall'))
