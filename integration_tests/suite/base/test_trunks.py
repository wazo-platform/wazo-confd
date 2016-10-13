# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

from test_api import scenarios as s
from test_api import fixtures
from test_api import confd

from hamcrest import (assert_that,
                      contains,
                      empty,
                      has_entries,
                      has_entry,
                      has_item,
                      is_not,
                      none,
                      not_)


def test_get_errors():
    fake_trunk = confd.trunks(999999).get
    yield s.check_resource_not_found, fake_trunk, 'Trunk'


def test_delete_errors():
    fake_trunk = confd.trunks(999999).delete
    yield s.check_resource_not_found, fake_trunk, 'Trunk'


def test_post_errors():
    url = confd.trunks.post
    for check in error_checks(url):
        yield check


@fixtures.trunk()
def test_put_errors(trunk):
    url = confd.trunks(trunk['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'context', 123
    yield s.check_bogus_field_returns_error, url, 'context', []
    yield s.check_bogus_field_returns_error, url, 'context', {}

    yield s.check_bogus_field_returns_error, url, 'context', 'invalid'


@fixtures.context(name='search')
@fixtures.context(name='hidden')
@fixtures.trunk(context='search')
@fixtures.trunk(context='hidden')
def test_search(_, __, trunk, hidden):
    url = confd.trunks
    searches = {'context': 'search'}

    for field, term in searches.items():
        yield check_search, url, trunk, hidden, field, term


def check_search(url, trunk, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, trunk[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: trunk[field]})

    expected = has_item(has_entry('id', trunk['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.context(name='sort1')
@fixtures.context(name='sort2')
@fixtures.trunk(context='sort1')
@fixtures.trunk(context='sort2')
def test_sorting(_, __, trunk1, trunk2):
    yield check_sorting, trunk1, trunk2, 'context', 'sort'


def check_sorting(trunk1, trunk2, field, search):
    response = confd.trunks.get(search=search, order=field, direction='asc')
    assert_that(response.items, contains(has_entries(id=trunk1['id']),
                                         has_entries(id=trunk2['id'])))

    response = confd.trunks.get(search=search, order=field, direction='desc')
    assert_that(response.items, contains(has_entries(id=trunk2['id']),
                                         has_entries(id=trunk1['id'])))


@fixtures.trunk()
def test_get(trunk):
    response = confd.trunks(trunk['id']).get()
    assert_that(response.item, has_entries(id=trunk['id'],
                                           context=trunk['context'],
                                           endpoint_sip=none(),
                                           endpoint_custom=none(),
                                           outcalls=empty()))


def test_create_minimal_parameters():
    response = confd.trunks.post()
    response.assert_created('trunks')

    assert_that(response.item, has_entries(id=not_(empty())))


@fixtures.context()
def test_create_all_parameters(context):
    response = confd.trunks.post(context=context['name'])
    response.assert_created('trunks')

    assert_that(response.item, has_entries(context=context['name']))


@fixtures.trunk()
def test_edit_minimal_parameters(trunk):
    parameters = {}

    response = confd.trunks(trunk['id']).put(**parameters)
    response.assert_updated()


@fixtures.context(name='not_default')
@fixtures.trunk()
def test_edit_all_parameters(context, trunk):
    parameters = {'context': context['name']}

    response = confd.trunks(trunk['id']).put(**parameters)
    response.assert_updated()

    response = confd.trunks(trunk['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.trunk()
def test_delete(trunk):
    response = confd.trunks(trunk['id']).delete()
    response.assert_deleted()
