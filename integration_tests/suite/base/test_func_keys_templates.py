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

from test_api import scenarios as s
from test_api import fixtures
from test_api import confd

from hamcrest import (assert_that,
                      contains,
                      has_entries,
                      has_entry,
                      has_item,
                      is_not)

invalid_destinations = [
    1234,
    'string',
    {'type': 'not_valid'},

    {'type': 'user'},
    {'type': 'user', 'bad_field': 123},
    {'type': 'user', 'user_id': 'string'},
    {'type': 'user', 'user_id': None},

    {'type': 'group'},
    {'type': 'group', 'bad_field': 123},
    {'type': 'group', 'group_id': 'string'},
    {'type': 'group', 'group_id': None},

    {'type': 'queue'},
    {'type': 'queue', 'bad_field': 123},
    {'type': 'queue', 'queue_id': 'string'},
    {'type': 'queue', 'queue_id': None},

    {'type': 'conference'},
    {'type': 'conference', 'bad_field': 123},
    {'type': 'conference', 'conference_id': 'string'},
    {'type': 'conference', 'conference_id': None},

    {'type': 'custom'},
    {'type': 'custom', 'bad_field': '123'},
    {'type': 'custom', 'exten': 1234},
    {'type': 'custom', 'exten': True},
    {'type': 'custom', 'exten': None},

    {'type': 'service'},
    {'type': 'service', 'bad_field': 'enablevm'},
    {'type': 'service', 'service': 'not_valid'},
    {'type': 'service', 'service': True},
    {'type': 'service', 'service': None},
    {'type': 'service', 'service': 1234},

    {'type': 'forward'},
    {'type': 'forward', 'bad_field': 'busy'},
    {'type': 'forward', 'forward': 'not_valid'},
    {'type': 'forward', 'forward': True},
    {'type': 'forward', 'forward': None},
    {'type': 'forward', 'forward': 1234},
    {'type': 'forward', 'forward': 'busy', 'exten': True},
    {'type': 'forward', 'forward': 'busy', 'exten': 1234},

    {'type': 'transfer'},
    {'type': 'transfer', 'bad_field': 'blind'},
    {'type': 'transfer', 'transfer': 'not_valid'},
    {'type': 'transfer', 'transfer': True},
    {'type': 'transfer', 'transfer': None},
    {'type': 'transfer', 'transfer': 1234},

    {'type': 'park_position'},
    {'type': 'park_position', 'bad_field': 123},
    {'type': 'park_position', 'position': 'not_valid'},
    {'type': 'park_position', 'position': None},

    # This type are exclude from template
    {'type': 'agent'},
    {'type': 'agent', 'agent_id': 1234},

    # This type are exclude from template
    {'type': 'bsfilter'},
    {'type': 'bsfilter', 'filter_member_id': 1234},

    {'type': 'paging'},
    {'type': 'paging', 'bad_field': 123},
    {'type': 'paging', 'paging_id': 'not_valid'},
    {'type': 'paging', 'paging_id': None},

]


def test_get_errors():
    fake_get = confd.funckeys.templates(999999).get
    yield s.check_resource_not_found, fake_get, 'FuncKeyTemplate'


def test_post_errors():
    url = confd.funckeys.templates.post
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'keys', True
    yield s.check_bogus_field_returns_error, url, 'keys', None
    yield s.check_bogus_field_returns_error, url, 'keys', 'string'
    yield s.check_bogus_field_returns_error, url, 'keys', 1234

    for destination in invalid_destinations:
        yield s.check_bogus_field_returns_error, url, 'keys', {'1': {'destination': destination}}


@fixtures.funckey_template()
def test_get_position_errors(funckey_template):
    fake_get = confd.funckeys.templates(funckey_template['id'])(1).get
    yield s.check_resource_not_found, fake_get, 'FuncKey'


# Should raise an error
# @fixtures.funckey_template()
# def test_delete_position_errors(funckey_template):
#     fake_delete = confd.funckeys.templates(funckey_template['id'])(1).delete
#     yield s.check_resource_not_found, fake_delete, 'FuncKey'


@fixtures.funckey_template()
def test_put_position_errors(funckey_template):
    url = confd.funckeys.templates(funckey_template['id'])(1).put
    for check in error_position_checks(url):
        yield check


def error_position_checks(url):
    yield s.check_bogus_field_returns_error, url, 'blf', 123
    yield s.check_bogus_field_returns_error, url, 'blf', 'string'
    yield s.check_bogus_field_returns_error, url, 'blf', None
    yield s.check_bogus_field_returns_error, url, 'label', 1234

    for destination in invalid_destinations:
        yield s.check_bogus_field_returns_error, url, 'destination', destination


@fixtures.funckey_template(name="search")
@fixtures.funckey_template(name="hidden")
def test_search_on_funckey_template(funckey_template, hidden):
    url = confd.funckeys.templates
    searches = {'name': 'search'}

    for field, term in searches.items():
        yield check_search, url, funckey_template, hidden, field, term


def check_search(url, funckey_template, hidden, field, term):
    response = url.get(search=term)

    shows_expected_funckey_template = has_item(has_entry(field, funckey_template[field]))
    discards_hidden_funckey_template = is_not(has_item(has_entry(field, hidden[field])))
    assert_that(response.items, shows_expected_funckey_template)
    assert_that(response.items, discards_hidden_funckey_template)


@fixtures.funckey_template(name='sort1')
@fixtures.funckey_template(name='sort2')
def test_funckey_template_sorting(funckey_template1, funckey_template2):
    yield check_funckey_template_sorting, funckey_template1, funckey_template2, 'name', 'sort'


def check_funckey_template_sorting(funckey_template1, funckey_template2, field, search):
    response = confd.funckeys.templates.get(search=search, order=field, direction='asc')
    assert_that(response.items, contains(has_entries(id=funckey_template1['id']),
                                         has_entries(id=funckey_template2['id'])))

    response = confd.funckeys.templates.get(search=search, order=field, direction='desc')
    assert_that(response.items, contains(has_entries(id=funckey_template2['id']),
                                         has_entries(id=funckey_template1['id'])))


@fixtures.funckey_template(name='template')
def test_get(funckey_template):
    response = confd.funckeys.templates(funckey_template['id']).get()
    assert_that(response.item, has_entries(name='template'))


@fixtures.funckey_template(keys={'3': {'destination': {'type': 'custom', 'exten': '123'}}})
def test_get_position(funckey_template):
    response = confd.funckeys.templates(funckey_template['id'])(3).get()
    assert_that(response.item['destination'], has_entries(type='custom', exten='123'))


@fixtures.funckey_template()
def test_delete(funckey_template):
    response = confd.funckeys.templates(funckey_template['id']).delete()
    response.assert_deleted()
    url_get = confd.funckeys.templates(funckey_template['id']).get
    s.check_resource_not_found(url_get, 'FuncKeyTemplate')


@fixtures.funckey_template(keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}})
def test_delete_position(funckey_template):
    response = confd.funckeys.templates(funckey_template['id'])(1).delete()
    response.assert_deleted()
    url_get = confd.funckeys.templates(funckey_template['id'])(1).get
    s.check_resource_not_found(url_get, 'FuncKey')


def test_create_funckey_template_minimal_parameters():
    response = confd.funckeys.templates.post()
    response.assert_created('templates')

    assert_that(response.item, has_entries(keys={},
                                           name=None))


def test_post_error_on_duplicate_destination():
    parameters = {'name': 'duplicate_dest',
                  'keys': {'1': {'destination': {'type': 'custom', 'exten': '123'}},
                           '2': {'destination': {'type': 'custom', 'exten': '123'}}}}

    response = confd.funckeys.templates.post(**parameters)
    response.assert_status(400)


@fixtures.funckey_template(keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}})
def test_put_error_on_duplicate_destination(funckey_template):
    destination = {'destination': {'type': 'custom', 'exten': '123'}}

    response = confd.funckeys.templates(funckey_template['id'])(2).put(destination)
    response.assert_status(400)


def test_create_funckey_template_all_parameters():
    # Done in test_func_keys.py
    pass


def test_edit_funckey_template_position_all_parameters():
    # Done in test_func_keys.py
    pass
