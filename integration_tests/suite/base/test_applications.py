# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    all_of,
    assert_that,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    not_,
    not_none,
)

from . import confd
from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)

FAKE_UUID = '00000000-0000-0000-0000-000000000000'


def test_get_errors():
    fake_application = confd.applications(FAKE_UUID).get
    yield s.check_resource_not_found, fake_application, 'Application'


def test_delete_errors():
    fake_application = confd.applications(FAKE_UUID).delete
    yield s.check_resource_not_found, fake_application, 'Application'


def test_post_errors():
    url = confd.applications.post
    for check in error_checks(url):
        yield check


@fixtures.application()
def test_put_errors(application):
    url = confd.applications(application['uuid']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', 1234
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'destination', True
    yield s.check_bogus_field_returns_error, url, 'destination', 1234
    yield s.check_bogus_field_returns_error, url, 'destination', 'invalid choice'
    yield s.check_bogus_field_returns_error, url, 'destination', []
    yield s.check_bogus_field_returns_error, url, 'destination', {}


@fixtures.application(name='search')
@fixtures.application(name='hidden')
def test_search(application, hidden):
    url = confd.applications
    searches = {
        'name': 'search',
    }

    for field, term in searches.items():
        yield check_search, url, application, hidden, field, term


def check_search(url, application, hidden, field, term):
    response = url.get(search=term)

    expected = has_item(has_entry(field, application[field]))
    not_expected = has_item(has_entry(field, hidden[field]))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))

    response = url.get(**{field: application[field]})

    expected = has_item(has_entry('uuid', application['uuid']))
    not_expected = has_item(has_entry('uuid', hidden['uuid']))
    assert_that(response.items, expected)
    assert_that(response.items, is_not(not_expected))


@fixtures.application(name='sort1')
@fixtures.application(name='sort2')
def test_sort_offset_limit(application1, application2):
    url = confd.applications.get
    id_field = 'uuid'
    yield s.check_sorting, url, application1, application2, 'name', 'sort', id_field

    yield s.check_offset, url, application1, application2, 'name', 'sort', id_field
    yield s.check_offset_legacy, url, application1, application2, 'name', 'sort', id_field

    yield s.check_limit, url, application1, application2, 'name', 'sort', id_field


@fixtures.application(wazo_tenant=MAIN_TENANT)
@fixtures.application(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.applications.get(wazo_tenant=MAIN_TENANT)
    assert_that(
        response.items,
        all_of(has_item(main)), not_(has_item(sub)),
    )

    response = confd.applications.get(wazo_tenant=SUB_TENANT)
    assert_that(
        response.items,
        all_of(has_item(sub), not_(has_item(main))),
    )

    response = confd.applications.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(
        response.items,
        has_items(main, sub),
    )


@fixtures.application()
def test_get(application):
    response = confd.applications(application['uuid']).get()
    assert_that(response.item, has_entries(
        uuid=application['uuid'],
        name=application['name'],
        destination=application['destination'],
        destination_options=application['destination_options'],
    ))


@fixtures.application(wazo_tenant=MAIN_TENANT)
@fixtures.application(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.applications(main['uuid']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Application'))

    response = confd.applications(sub['uuid']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.applications.post()
    response.assert_created('applications')

    assert_that(response.item, has_entries(
        uuid=not_none(),
        tenant_uuid=MAIN_TENANT,
        destination=None,
        destination_options={},
    ))

    confd.applications(response.item['uuid']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'name': 'MyApplication',
        'destination': 'node',
        'destination_options': {
            'type': 'holding',
            'music_on_hold': 'default',
        }
    }

    response = confd.applications.post(**parameters)
    response.assert_created('applications')
    response = confd.applications(response.item['uuid']).get()

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.applications(response.item['uuid']).delete().assert_deleted()


@fixtures.application()
def test_edit_minimal_parameters(application):
    response = confd.applications(application['uuid']).put()
    response.assert_updated()


@fixtures.application()
def test_edit_all_parameters(application):
    parameters = {
        'name': 'UpdatedApplication',
        'destination': 'node',
        'destination_options': {
            'type': 'holding',
            'music_on_hold': 'updated_moh',
        }
    }

    response = confd.applications(application['uuid']).put(**parameters)
    response.assert_updated()

    response = confd.applications(application['uuid']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.application(destination='node', destination_options={'type': 'holding'})
def test_edit_remove_destination(application):
    parameters = {
        'destination': None,
        'destination_options': {},
    }

    response = confd.applications(application['uuid']).put(**parameters)
    response.assert_updated()

    response = confd.applications(application['uuid']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.application(wazo_tenant=MAIN_TENANT)
@fixtures.application(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.applications(main['uuid']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Application'))

    response = confd.applications(sub['uuid']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.application()
def test_delete(application):
    response = confd.applications(application['uuid']).delete()
    response.assert_deleted()
    response = confd.applications(application['uuid']).get()
    response.assert_match(404, e.not_found(resource='Application'))


@fixtures.application(wazo_tenant=MAIN_TENANT)
@fixtures.application(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.applications(main['uuid']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Application'))

    response = confd.applications(sub['uuid']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.application()
def test_bus_events(application):
    yield s.check_bus_event, 'config.applications.created', confd.applications.post
    yield s.check_bus_event, 'config.applications.edited', confd.applications(application['uuid']).put
    yield s.check_bus_event, 'config.applications.deleted', confd.applications(application['uuid']).delete
