# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s

from hamcrest import (
    assert_that,
    empty,
    has_entries,
    has_entry,
    has_item,
    is_not,
    not_,
)
from . import confd

MAIN_TENANT = 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee1'


def test_get_errors():
    fake_outcall = confd.outcalls(999999).get
    yield s.check_resource_not_found, fake_outcall, 'Outcall'


def test_delete_errors():
    fake_outcall = confd.outcalls(999999).delete
    yield s.check_resource_not_found, fake_outcall, 'Outcall'


def test_post_errors():
    url = confd.outcalls.post
    for check in error_checks(url):
        yield check


@fixtures.outcall()
def test_put_errors(outcall):
    url = confd.outcalls(outcall['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', 123
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', s.random_string(40)
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', []
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', {}
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', 1234
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'internal_caller_id', 1234
    yield s.check_bogus_field_returns_error, url, 'internal_caller_id', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'internal_caller_id', None
    yield s.check_bogus_field_returns_error, url, 'internal_caller_id', []
    yield s.check_bogus_field_returns_error, url, 'internal_caller_id', {}
    yield s.check_bogus_field_returns_error, url, 'ring_time', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'ring_time', []
    yield s.check_bogus_field_returns_error, url, 'ring_time', {}
    yield s.check_bogus_field_returns_error, url, 'description', 1234
    yield s.check_bogus_field_returns_error, url, 'description', []
    yield s.check_bogus_field_returns_error, url, 'description', {}
    yield s.check_bogus_field_returns_error, url, 'enabled', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'enabled', None
    yield s.check_bogus_field_returns_error, url, 'enabled', []
    yield s.check_bogus_field_returns_error, url, 'enabled', {}

    for check in unique_error_checks(url):
        yield check


@fixtures.outcall(name='unique')
def unique_error_checks(url, outcall):
    yield s.check_bogus_field_returns_error, url, 'name', outcall['name']


@fixtures.outcall(description='search')
@fixtures.outcall(description='hidden')
def test_search(outcall, hidden):
    url = confd.outcalls
    searches = {'description': 'search'}

    for field, term in searches.items():
        yield check_search, url, outcall, hidden, field, term


def check_search(url, outcall, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, outcall[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: outcall[field]})

    expected = has_item(has_entry('id', outcall['id']))
    not_expected = has_item(has_entry('id', hidden['id']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.outcall(description='sort1')
@fixtures.outcall(description='sort2')
def test_sorting_offset_limit(outcall1, outcall2):
    url = confd.outcalls.get
    yield s.check_sorting, url, outcall1, outcall2, 'description', 'sort'

    yield s.check_offset, url, outcall1, outcall2, 'description', 'sort'
    yield s.check_offset_legacy, url, outcall1, outcall2, 'description', 'sort'

    yield s.check_limit, url, outcall1, outcall2, 'description', 'sort'


@fixtures.outcall()
def test_get(outcall):
    response = confd.outcalls(outcall['id']).get()
    assert_that(
        response.item,
        has_entries(
            id=outcall['id'],
            tenant_uuid=MAIN_TENANT,
            preprocess_subroutine=outcall['preprocess_subroutine'],
            description=outcall['description'],
            internal_caller_id=outcall['internal_caller_id'],
            name=outcall['name'],
            ring_time=outcall['ring_time'],
            trunks=empty(),
        ))


def test_create_minimal_parameters():
    response = confd.outcalls.post(name='MyOutcall')
    response.assert_created('outcalls')

    assert_that(
        response.item,
        has_entries(
            id=not_(empty()),
            tenant_uuid=MAIN_TENANT,
        ))

    confd.outcalls(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {'name': 'MyOutcall',
                  'internal_caller_id': True,
                  'preprocess_subroutine': 'subroutine',
                  'ring_time': 10,
                  'description': 'outcall description',
                  'enabled': False}

    response = confd.outcalls.post(**parameters)
    response.assert_created('outcalls')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.outcalls(response.item['id']).delete().assert_deleted()


@fixtures.outcall()
def test_edit_minimal_parameters(outcall):
    response = confd.outcalls(outcall['id']).put()
    response.assert_updated()


@fixtures.outcall()
def test_edit_all_parameters(outcall):
    parameters = {'name': 'MyOutcall',
                  'internal_caller_id': True,
                  'preprocess_subroutine': 'subroutine',
                  'ring_time': 10,
                  'description': 'outcall description',
                  'enabled': False}

    response = confd.outcalls(outcall['id']).put(**parameters)
    response.assert_updated()

    response = confd.outcalls(outcall['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.outcall()
def test_delete(outcall):
    response = confd.outcalls(outcall['id']).delete()
    response.assert_deleted()
    response = confd.outcalls(outcall['id']).get()
    response.assert_match(404, e.not_found(resource='Outcall'))


@fixtures.outcall()
def test_bus_events(outcall):
    yield s.check_bus_event, 'config.outcalls.created', confd.outcalls.post, {'name': 'a'}
    yield s.check_bus_event, 'config.outcalls.edited', confd.outcalls(outcall['id']).put
    yield s.check_bus_event, 'config.outcalls.deleted', confd.outcalls(outcall['id']).delete
