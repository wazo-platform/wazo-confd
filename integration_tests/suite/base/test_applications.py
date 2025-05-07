# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd

FAKE_UUID = '00000000-0000-0000-0000-000000000000'


def test_get_errors():
    fake_application = confd.applications(FAKE_UUID).get
    s.check_resource_not_found(fake_application, 'Application')


def test_delete_errors():
    fake_application = confd.applications(FAKE_UUID).delete
    s.check_resource_not_found(fake_application, 'Application')


def test_post_errors():
    url = confd.applications.post
    error_checks(url)


@fixtures.application()
def test_put_errors(application):
    url = confd.applications(application['uuid']).put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', 1234)
    s.check_bogus_field_returns_error(url, 'name', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'name', {})
    s.check_bogus_field_returns_error(url, 'destination', True)
    s.check_bogus_field_returns_error(url, 'destination', 1234)
    s.check_bogus_field_returns_error(url, 'destination', 'invalid choice')
    s.check_bogus_field_returns_error(url, 'destination', [])
    s.check_bogus_field_returns_error(url, 'destination', {})


@fixtures.application(name='search')
@fixtures.application(name='hidden')
def test_search(application, hidden):
    url = confd.applications
    searches = {'name': 'search'}

    for field, term in searches.items():
        check_search(url, application, hidden, field, term)


def check_search(url, application, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, application[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: application[field]})
    assert_that(response.items, has_item(has_entry('uuid', application['uuid'])))
    assert_that(response.items, is_not(has_item(has_entry('uuid', hidden['uuid']))))


@fixtures.application(name='sort1')
@fixtures.application(name='sort2')
def test_sort_offset_limit(application1, application2):
    url = confd.applications.get
    id_field = 'uuid'
    s.check_sorting(url, application1, application2, 'name', 'sort', id_field)
    s.check_offset(url, application1, application2, 'name', 'sort', id_field)
    s.check_limit(url, application1, application2, 'name', 'sort', id_field)


@fixtures.application(wazo_tenant=MAIN_TENANT)
@fixtures.application(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.applications.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.applications.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.applications.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.application()
def test_get(application):
    response = confd.applications(application['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            uuid=application['uuid'],
            name=application['name'],
            destination=application['destination'],
            destination_options=application['destination_options'],
        ),
    )


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

    assert_that(
        response.item,
        has_entries(
            uuid=not_none(),
            tenant_uuid=MAIN_TENANT,
            destination=None,
            destination_options={},
        ),
    )

    confd.applications(response.item['uuid']).delete().assert_deleted()


def test_create_minimal_node_parameters():
    response = confd.applications.post(
        destination='node', destination_options={'type': 'holding'}
    )
    response.assert_created('applications')

    assert_that(
        response.item,
        has_entries(
            uuid=not_none(),
            tenant_uuid=MAIN_TENANT,
            destination='node',
            destination_options=has_entries(
                type='holding', music_on_hold=None, answer=False
            ),
        ),
    )

    confd.applications(response.item['uuid']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'name': 'MyApplication',
        'destination': 'node',
        'destination_options': {
            'type': 'holding',
            'music_on_hold': 'default',
            'answer': True,
        },
    }

    response = confd.applications.post(**parameters)
    response.assert_created('applications')
    response = confd.applications(response.item['uuid']).get()

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.applications(response.item['uuid']).delete().assert_deleted()


@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_create_with_moh(main_moh, sub_moh):
    parameters_main = {
        'name': 'MainApplication',
        'destination': 'node',
        'destination_options': {
            'type': 'holding',
            'music_on_hold': sub_moh['name'],
        },
    }
    parameters_sub = {
        'name': 'SubApplication',
        'destination': 'node',
        'destination_options': {
            'type': 'holding',
            'music_on_hold': main_moh['name'],
        },
    }
    response = confd.applications.post(**parameters_main, wazo_tenant=SUB_TENANT)
    response.assert_created('applications')
    confd.applications(response.item['uuid']).delete().assert_deleted()

    response = confd.applications.post(**parameters_sub)
    response.assert_created('applications')
    confd.applications(response.item['uuid']).delete().assert_deleted()

    response = confd.applications.post(**parameters_main)
    response.assert_match(400, e.not_found(resource='MOH'))

    response = confd.applications.post(**parameters_sub, wazo_tenant=SUB_TENANT)
    response.assert_match(400, e.not_found(resource='MOH'))


@fixtures.application()
def test_edit_minimal_parameters(application):
    response = confd.applications(application['uuid']).put()
    response.assert_updated()


@fixtures.application()
@fixtures.moh(label='updated_moh')
def test_edit_all_parameters(application, moh):
    parameters = {
        'name': 'UpdatedApplication',
        'destination': 'node',
        'destination_options': {
            'type': 'holding',
            'music_on_hold': moh['name'],
            'answer': True,
        },
    }

    response = confd.applications(application['uuid']).put(**parameters)
    response.assert_updated()

    response = confd.applications(application['uuid']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.application(destination='node', destination_options={'type': 'holding'})
def test_edit_remove_destination(application):
    parameters = {'destination': None, 'destination_options': {}}

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


@fixtures.application(
    destination='node',
    destination_options={'type': 'holding'},
    wazo_tenant=MAIN_TENANT,
)
@fixtures.application(
    destination='node',
    destination_options={'type': 'holding'},
    wazo_tenant=SUB_TENANT,
)
@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant_moh(main, sub, main_moh, sub_moh):
    parameters = {
        'destination': 'node',
        'destination_options': {'type': 'holding', 'music_on_hold': main_moh['name']},
    }

    response = confd.applications(sub['uuid']).put(**parameters)
    response.assert_match(400, e.not_found(resource='MOH'))

    response = confd.applications(main['uuid']).put(**parameters)
    response.assert_updated()

    parameters['destination_options']['music_on_hold'] = sub_moh['name']

    response = confd.applications(main['uuid']).put(**parameters)
    response.assert_match(400, e.not_found(resource='MOH'))

    response = confd.applications(sub['uuid']).put(**parameters)
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
    url = confd.applications(application['uuid'])
    expected_headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event('application_created', expected_headers, confd.applications.post)
    s.check_event('application_edited', expected_headers, url.put)
    s.check_event('application_deleted', expected_headers, url.delete)
