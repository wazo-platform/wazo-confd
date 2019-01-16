# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s

from hamcrest import (assert_that,
                      contains,
                      empty,
                      has_entries,
                      has_item,
                      has_entry,
                      is_not,
                      not_)

NOT_FOUND_SWITCHBOARD_UUID = 'uuid-not-found'


def test_get_errors():
    fake_switchboard = confd.switchboards(NOT_FOUND_SWITCHBOARD_UUID).get
    yield s.check_resource_not_found, fake_switchboard, 'Switchboard'


def test_delete_errors():
    fake_switchboard = confd.switchboards(NOT_FOUND_SWITCHBOARD_UUID).delete
    yield s.check_resource_not_found, fake_switchboard, 'Switchboard'


def test_post_errors():
    url = confd.switchboards.post
    for check in error_checks(url):
        yield check


@fixtures.switchboard()
def test_put_errors(switchboard):
    fake_switchboard = confd.switchboards(NOT_FOUND_SWITCHBOARD_UUID).put
    yield s.check_resource_not_found, fake_switchboard, 'Switchboard'

    url = confd.switchboards(switchboard['uuid']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}


@fixtures.switchboard(name='hidden', preprocess_subroutine='hidden')
@fixtures.switchboard(name='search', preprocess_subroutine='search')
def test_search(hidden, switchboard):
    url = confd.switchboards
    searches = {'name': 'search'}

    for field, term in searches.items():
        yield check_search, url, switchboard, hidden, field, term


def check_search(url, switchboard, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, switchboard[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: switchboard[field]})

    expected = has_item(has_entry('uuid', switchboard['uuid']))
    not_expected = has_item(has_entry('uuid', hidden['uuid']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.switchboard(name='sort1')
@fixtures.switchboard(name='sort2')
def test_sorting(switchboard1, switchboard2):
    yield check_sorting, switchboard1, switchboard2, 'name', 'sort'


def check_sorting(switchboard1, switchboard2, field, search):
    response = confd.switchboards.get(search=search, order=field, direction='asc')
    assert_that(response.items, contains(has_entries(uuid=switchboard1['uuid']),
                                         has_entries(uuid=switchboard2['uuid'])))

    response = confd.switchboards.get(search=search, order=field, direction='desc')
    assert_that(response.items, contains(has_entries(uuid=switchboard2['uuid']),
                                         has_entries(uuid=switchboard1['uuid'])))


@fixtures.switchboard()
def test_get(switchboard):
    response = confd.switchboards(switchboard['uuid']).get()
    assert_that(response.item, has_entries(uuid=switchboard['uuid'],
                                           name=switchboard['name']))


def test_create_minimal_parameters():
    response = confd.switchboards.post(name='MySwitchboard')
    response.assert_created('switchboards')

    assert_that(response.item, has_entries(uuid=not_(empty()),
                                           name='MySwitchboard'))

    confd.switchboards(response.item['uuid']).delete().assert_deleted()


@fixtures.switchboard(name='before_edit')
def test_edit_minimal_parameters(switchboard):
    response = confd.switchboards(switchboard['uuid']).put(name='after_edit')
    response.assert_updated()

    expected = {'name': 'after_edit'}
    response = confd.switchboards(switchboard['uuid']).get()
    assert_that(response.item, has_entries(expected))


@fixtures.switchboard()
def test_delete(switchboard):
    response = confd.switchboards(switchboard['uuid']).delete()
    response.assert_deleted()
    response = confd.switchboards(switchboard['uuid']).get()
    response.assert_match(404, e.not_found(resource='Switchboard'))


@fixtures.switchboard()
def test_bus_events(switchboard):
    yield s.check_bus_event, 'config.switchboards.*.created', confd.switchboards.post, {'name': 'bus_event'}
    yield s.check_bus_event, 'config.switchboards.{uuid}.edited'.format(uuid=switchboard['uuid']), confd.switchboards(switchboard['uuid']).put
    yield s.check_bus_event, 'config.switchboards.{uuid}.deleted'.format(uuid=switchboard['uuid']), confd.switchboards(switchboard['uuid']).delete
