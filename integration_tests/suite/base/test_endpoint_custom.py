# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    has_entries,
    has_entry,
    has_items,
    instance_of,
    not_
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


def test_get_errors():
    fake_custom_get = confd.endpoints.custom(999999).get
    s.check_resource_not_found(fake_custom_get, 'CustomEndpoint')


def test_delete_errors():
    fake_custom = confd.endpoints.custom(999999).delete
    s.check_resource_not_found(fake_custom, 'CustomEndpoint')


def test_post_errors():
    url = confd.endpoints.custom.post
    error_checks(url)


def test_put_errors():
    with fixtures.custom() as custom:
        url = confd.endpoints.custom(custom['id']).put

        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'interface', None)
    s.check_bogus_field_returns_error(url, 'interface', True)
    s.check_bogus_field_returns_error(url, 'interface', 'custom/&&&~~~')
    s.check_bogus_field_returns_error(url, 'interface', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'interface', [])
    s.check_bogus_field_returns_error(url, 'interface', {})
    s.check_bogus_field_returns_error(url, 'interface_suffix', True)
    s.check_bogus_field_returns_error(url, 'interface_suffix', s.random_string(33))
    s.check_bogus_field_returns_error(url, 'interface_suffix', [])
    s.check_bogus_field_returns_error(url, 'interface_suffix', {})
    s.check_bogus_field_returns_error(url, 'enabled', None)
    s.check_bogus_field_returns_error(url, 'enabled', 'string')
    s.check_bogus_field_returns_error(url, 'enabled', [])
    s.check_bogus_field_returns_error(url, 'enabled', {})


def test_get():
    with fixtures.custom() as custom:
        response = confd.endpoints.custom(custom['id']).get()
        assert_that(response.item, has_entries({
            'id': instance_of(int),
            'interface': custom['interface'],
            'interface_suffix': custom['interface_suffix'],
            'enabled': True,
            'trunk': None,
            'line': None,
        }))



def test_list():
    with fixtures.custom() as custom1, fixtures.custom() as custom2:
        response = confd.endpoints.custom.get()
        assert_that(response.items, has_items(
            has_entry('id', custom1['id']),
            has_entry('id', custom2['id']),
        ))



def test_list_multi_tenant():
    with fixtures.custom(wazo_tenant=MAIN_TENANT) as main, fixtures.custom(wazo_tenant=SUB_TENANT) as sub:
        response = confd.endpoints.custom.get(wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            all_of(has_items(main)), not_(has_items(sub)),
        )

        response = confd.endpoints.custom.get(wazo_tenant=SUB_TENANT)
        assert_that(
            response.items,
            all_of(has_items(sub), not_(has_items(main))),
        )

        response = confd.endpoints.custom.get(wazo_tenant=MAIN_TENANT, recurse=True)
        assert_that(
            response.items,
            has_items(main, sub),
        )



def test_get_multi_tenant():
    with fixtures.custom(wazo_tenant=MAIN_TENANT) as main, fixtures.custom(wazo_tenant=SUB_TENANT) as sub:
        response = confd.endpoints.custom(main['id']).get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='CustomEndpoint'))

        response = confd.endpoints.custom(sub['id']).get(wazo_tenant=MAIN_TENANT)
        assert_that(response.item, has_entries(**sub))



def test_create_minimal_parameters():
    response = confd.endpoints.custom.post(interface='custom/createmin')

    response.assert_created('endpoint_custom', location='endpoints/custom')
    assert_that(response.item, has_entries({
        'id': instance_of(int),
        'tenant_uuid': MAIN_TENANT,
        'interface': 'custom/createmin',
        'enabled': True,
    }))


def test_create_all_parameters():
    response = confd.endpoints.custom.post(interface='custom/createall', enabled=False)

    response.assert_created('endpoint_custom', location='endpoints/custom')
    assert_that(response.item, has_entries({
        'id': instance_of(int),
        'tenant_uuid': MAIN_TENANT,
        'interface': 'custom/createall',
        'enabled': False
    }))


def test_create_interface_accept_uppercase_interface():
    response = confd.endpoints.custom.post(interface='Local/123@foobar')
    response.assert_ok()


def test_given_interface_already_exists_then_error_raised():
    response = confd.endpoints.custom.post(interface='custom/duplicate')
    response.assert_ok()

    response = confd.endpoints.custom.post(interface='custom/duplicate')
    response.assert_match(400, e.resource_exists('CustomEndpoint'))


def test_update():
    with fixtures.custom(interface='custom/beforeupdate') as custom:
        parameters = {
            'interface': 'custom/afterupdate',
            'interface_suffix': 'other',
            'enabled': False,
        }
        response = confd.endpoints.custom(custom['id']).put(**parameters)
        response.assert_updated()

        response = confd.endpoints.custom(custom['id']).get()
        assert_that(response.item, has_entries(**parameters))



def test_when_updating_custom_with_interface_that_already_exists_then_error_raised():
    with fixtures.custom() as custom, fixtures.custom(interface='custom/updateduplicate') as duplicate:
        response = confd.endpoints.custom(custom['id']).put(interface=duplicate['interface'])
        response.assert_match(400, e.resource_exists('CustomEndpoint'))



def test_when_updating_endpoint_then_values_are_not_overwriten_with_defaults():
    with fixtures.custom(enabled=False) as custom:
        response = confd.endpoints.custom(custom['id']).put(interface="noupdateoverwrite")
        response.assert_ok()

        custom = confd.endpoints.custom(custom['id']).get().item
        assert_that(custom, has_entries(enabled=False))



def test_edit_multi_tenant():
    with fixtures.custom(wazo_tenant=MAIN_TENANT) as main, fixtures.custom(wazo_tenant=SUB_TENANT) as sub:
        response = confd.endpoints.custom(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='CustomEndpoint'))

        response = confd.endpoints.custom(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()



def test_delete():
    with fixtures.custom() as custom:
        response = confd.endpoints.custom(custom['id']).delete()
        response.assert_deleted()



def test_delete_multi_tenant():
    with fixtures.custom(wazo_tenant=MAIN_TENANT) as main, fixtures.custom(wazo_tenant=SUB_TENANT) as sub:
        response = confd.endpoints.custom(main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='CustomEndpoint'))

        response = confd.endpoints.custom(sub['id']).delete(wazo_tenant=MAIN_TENANT)
        response.assert_deleted()

