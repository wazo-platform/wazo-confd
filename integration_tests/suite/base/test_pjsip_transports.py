# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_entries,
    has_items,
    is_not,
    empty,
    not_none,
)
from . import confd
from ..helpers import errors as e, fixtures, scenarios as s

FAKE_UUID = '99999999-9999-4999-9999-999999999999'


def test_post_errors():
    url = confd.sip.transports.post
    for check in error_checks(url):
        yield check

    for check in unique_error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'options', 123, {'name': 'transport'}
    yield s.check_bogus_field_returns_error, url, 'options', None, {'name': 'transport'}
    yield s.check_bogus_field_returns_error, url, 'options', True, {'name': 'transport'}
    yield s.check_bogus_field_returns_error, url, 'options', {}, {'name': 'transport'}
    yield s.check_bogus_field_returns_error, url, 'options', [
        ['not-a-transport-option', '42'],
    ], {'name': 'transport'}
    yield s.check_bogus_field_returns_error, url, 'options', [
        ['one', 'two', 'three']
    ], {'name': 'transport'}


def test_create_minimal_parameters():
    response = confd.sip.transports.post(name='my-transport')
    response.assert_created()

    assert_that(
        response.item,
        has_entries(uuid=not_none(), name='my-transport', options=empty(),),
    )

    confd.sip.transports(response.item['uuid']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'name': 'my-transport',
        'options': [
            ['bind', '0.0.0.0:5060'],
            ['local_net', '192.168.0.0/16'],
            ['local_net', '10.37.1.0/24'],
        ],
    }
    response = confd.sip.transports.post(parameters)
    response.assert_created()

    assert_that(response.item, has_entries(parameters))

    confd.sip.transports(response.item['uuid']).delete().assert_deleted()


@fixtures.transport()
def test_put_errors(transport):
    url = confd.sip.transports(transport['uuid']).put
    for check in error_checks(url):
        yield check

    for check in unique_error_checks(url):
        yield check


@fixtures.transport()
def test_edit_minimal_parameters(transport):
    response = confd.sip.transports(transport['uuid']).put()
    response.assert_updated()


def test_get_errors():
    fake_transport = confd.sip.transports(FAKE_UUID).get
    yield s.check_resource_not_found, fake_transport, 'Transport'


@fixtures.transport()
def test_get(transport):
    response = confd.sip.transports(transport['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            uuid=transport['uuid'],
            name=transport['name'],
            options=transport['options'],
        ),
    )


def test_delete_errors():
    fake_transport = confd.sip.transports(FAKE_UUID).delete
    yield s.check_resource_not_found, fake_transport, 'Transport'


@fixtures.transport()
def test_delete(transport):
    response = confd.sip.transports(transport['uuid']).delete()
    response.assert_deleted()

    response = confd.sip.transports(transport['uuid']).get()
    response.assert_match(404, e.not_found(resource='Transport'))


@fixtures.transport(name='duplicate-me')
def unique_error_checks(url, transport):
    yield s.check_bogus_field_returns_error, url, 'name', transport['name']


@fixtures.transport(name='hidden')
@fixtures.transport(name='search')
def test_search(hidden, transport):
    url = confd.sip.transports
    searches = {'name': 'search'}

    for field, term in searches.items():
        yield check_search, url, transport, hidden, field, term


def check_search(url, transport, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_items(has_entries(field, transport[field])))
    assert_that(response.items, is_not(has_items(has_entries(field, hidden[field]))))

    response = url.get(**{field: transport[field]})
    assert_that(response.items, has_items(has_entries('uuid', transport['uuid'])))
    assert_that(response.items, is_not(has_items(has_entries('uuid', hidden['uuid']))))


@fixtures.transport(name='sort1')
@fixtures.transport(name='sort2')
def test_sorting_offset_limit(transport1, transport2):
    url = confd.sip.transports.get
    yield s.check_sorting, url, transport1, transport2, 'name', 'sort', 'uuid'

    yield s.check_offset, url, transport1, transport2, 'name', 'sort', 'uuid'

    yield s.check_limit, url, transport1, transport2, 'name', 'sort', 'uuid'


@fixtures.transport(name='original')
def test_bus_events(transport):
    yield s.check_bus_event, 'config.sip.transports.created', confd.sip.transports.post, {
        'name': 'a-leaked-transport',
    }
    yield s.check_bus_event, 'config.sip.transports.edited', confd.sip.transports(
        transport['uuid']
    ).put, {'name': 'new'}
    yield s.check_bus_event, 'config.sip.transports.deleted', confd.sip.transports(
        transport['uuid']
    ).delete
