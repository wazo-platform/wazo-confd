# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    none,
    not_,
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
    fake_group = confd.groups(999999).get
    s.check_resource_not_found(fake_group, 'Group')


def test_delete_errors():
    fake_group = confd.groups(999999).delete
    s.check_resource_not_found(fake_group, 'Group')


def test_post_errors():
    url = confd.groups.post
    error_checks(url)


def test_put_errors():
    with fixtures.group() as group:
        url = confd.groups(group['id']).put
        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'name', 123)
    s.check_bogus_field_returns_error(url, 'name', 'invalid regex')
    s.check_bogus_field_returns_error(url, 'name', 'general')
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', None)
    s.check_bogus_field_returns_error(url, 'name', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'name', {})
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', 123)
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', s.random_string(40))
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', [])
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', {})
    s.check_bogus_field_returns_error(url, 'ring_strategy', 123)
    s.check_bogus_field_returns_error(url, 'ring_strategy', 'invalid')
    s.check_bogus_field_returns_error(url, 'ring_strategy', True)
    s.check_bogus_field_returns_error(url, 'ring_strategy', None)
    s.check_bogus_field_returns_error(url, 'ring_strategy', [])
    s.check_bogus_field_returns_error(url, 'ring_strategy', {})
    s.check_bogus_field_returns_error(url, 'caller_id_mode', True)
    s.check_bogus_field_returns_error(url, 'caller_id_mode', 'invalid')
    s.check_bogus_field_returns_error(url, 'caller_id_mode', 1234)
    s.check_bogus_field_returns_error(url, 'caller_id_mode', [])
    s.check_bogus_field_returns_error(url, 'caller_id_mode', {})
    s.check_bogus_field_returns_error(url, 'caller_id_name', 1234)
    s.check_bogus_field_returns_error(url, 'caller_id_name', True)
    s.check_bogus_field_returns_error(url, 'caller_id_name', s.random_string(81))
    s.check_bogus_field_returns_error(url, 'caller_id_name', [])
    s.check_bogus_field_returns_error(url, 'caller_id_name', {})
    s.check_bogus_field_returns_error(url, 'music_on_hold', 123)
    s.check_bogus_field_returns_error(url, 'music_on_hold', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'music_on_hold', [])
    s.check_bogus_field_returns_error(url, 'music_on_hold', {})
    s.check_bogus_field_returns_error(url, 'user_timeout', 'ten')
    s.check_bogus_field_returns_error(url, 'user_timeout', -1)
    s.check_bogus_field_returns_error(url, 'user_timeout', {})
    s.check_bogus_field_returns_error(url, 'user_timeout', [])
    s.check_bogus_field_returns_error(url, 'retry_delay', 'ten')
    s.check_bogus_field_returns_error(url, 'retry_delay', -1)
    s.check_bogus_field_returns_error(url, 'retry_delay', {})
    s.check_bogus_field_returns_error(url, 'retry_delay', [])
    s.check_bogus_field_returns_error(url, 'timeout', 'ten')
    s.check_bogus_field_returns_error(url, 'timeout', -1)
    s.check_bogus_field_returns_error(url, 'timeout', {})
    s.check_bogus_field_returns_error(url, 'timeout', [])
    s.check_bogus_field_returns_error(url, 'ring_in_use', 'yeah')
    s.check_bogus_field_returns_error(url, 'ring_in_use', 123)
    s.check_bogus_field_returns_error(url, 'ring_in_use', {})
    s.check_bogus_field_returns_error(url, 'ring_in_use', [])
    s.check_bogus_field_returns_error(url, 'enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'enabled', 123)
    s.check_bogus_field_returns_error(url, 'enabled', {})
    s.check_bogus_field_returns_error(url, 'enabled', [])

    unique_error_checks(url)


def unique_error_checks(url):
    with fixtures.group(name='unique') as group, fixtures.queue(name='queue_name') as queue:
        s.check_bogus_field_returns_error(url, 'name', group['name'])
        s.check_bogus_field_returns_error(url, 'name', queue['name'])



def test_search():
    with fixtures.group(name='hidden', preprocess_subroutine='hidden') as hidden, fixtures.group(name='search', preprocess_subroutine='search') as group:
        url = confd.groups
        searches = {'name': 'search',
                    'preprocess_subroutine': 'search'}

        for field, term in searches.items():
            check_search(url, group, hidden, field, term)



def check_search(url, group, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, group[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: group[field]})
    assert_that(response.items, has_item(has_entry('id', group['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def test_list_multi_tenant():
    with fixtures.group(wazo_tenant=MAIN_TENANT) as main, fixtures.group(wazo_tenant=SUB_TENANT) as sub:
        response = confd.groups.get(wazo_tenant=MAIN_TENANT)
        assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

        response = confd.groups.get(wazo_tenant=SUB_TENANT)
        assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

        response = confd.groups.get(wazo_tenant=MAIN_TENANT, recurse=True)
        assert_that(response.items, has_items(main, sub))



def test_sorting_offset_limit():
    with fixtures.group(name='sort1', preprocess_subroutine='sort1') as group1, fixtures.group(name='sort2', preprocess_subroutine='sort2') as group2:
        url = confd.groups.get
        s.check_sorting(url, group1, group2, 'name', 'sort')
        s.check_sorting(url, group1, group2, 'preprocess_subroutine', 'sort')

        s.check_offset(url, group1, group2, 'name', 'sort')
        s.check_offset_legacy(url, group1, group2, 'name', 'sort')

        s.check_limit(url, group1, group2, 'name', 'sort')



def test_get():
    with fixtures.group() as group:
        response = confd.groups(group['id']).get()
        assert_that(response.item, has_entries(
            id=group['id'],
            name=group['name'],
            caller_id_mode=group['caller_id_mode'],
            caller_id_name=group['caller_id_name'],
            timeout=group['timeout'],
            music_on_hold=group['music_on_hold'],
            preprocess_subroutine=group['preprocess_subroutine'],
            ring_in_use=group['ring_in_use'],
            ring_strategy=group['ring_strategy'],
            user_timeout=group['user_timeout'],
            retry_delay=group['retry_delay'],
            enabled=group['enabled'],
            extensions=empty(),
            members=has_entries(
                users=empty(),
                extensions=empty(),
            ),
            incalls=empty(),
            fallbacks=has_entries(noanswer_destination=none())
        ))



def test_get_multi_tenant():
    with fixtures.group(wazo_tenant=MAIN_TENANT) as main, fixtures.group(wazo_tenant=SUB_TENANT) as sub:
        response = confd.groups(main['id']).get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Group'))

        response = confd.groups(sub['id']).get(wazo_tenant=MAIN_TENANT)
        assert_that(response.item, has_entries(**sub))



def test_create_minimal_parameters():
    response = confd.groups.post(name='MyGroup')
    response.assert_created('groups')

    assert_that(response.item, has_entries(id=not_(empty()),
                                           name='MyGroup',
                                           tenant_uuid=MAIN_TENANT))

    confd.groups(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {'name': 'MyGroup',
                  'caller_id_mode': 'prepend',
                  'caller_id_name': 'GROUP-',
                  'timeout': 42,
                  'music_on_hold': 'default',
                  'preprocess_subroutine': 'subroutien',
                  'ring_in_use': False,
                  'ring_strategy': 'weight_random',
                  'user_timeout': 24,
                  'retry_delay': 12,
                  'enabled': False}

    response = confd.groups.post(**parameters)
    response.assert_created('groups')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.groups(response.item['id']).delete().assert_deleted()


def test_create_multi_tenant():
    response = confd.groups.post(name='MyGroup', wazo_tenant=SUB_TENANT)
    response.assert_created('groups')

    assert_that(response.item, has_entries(tenant_uuid=SUB_TENANT))


def test_edit_minimal_parameters():
    with fixtures.group() as group:
        response = confd.groups(group['id']).put()
        response.assert_updated()



def test_edit_all_parameters():
    with fixtures.group() as group:
        parameters = {'name': 'MyGroup',
                      'caller_id_mode': 'prepend',
                      'caller_id_name': 'GROUP-',
                      'timeout': 42,
                      'music_on_hold': 'default',
                      'preprocess_subroutine': 'subroutien',
                      'ring_in_use': False,
                      'ring_strategy': 'random',
                      'user_timeout': 24,
                      'retry_delay': 12,
                      'enabled': False}

        response = confd.groups(group['id']).put(**parameters)
        response.assert_updated()

        response = confd.groups(group['id']).get()
        assert_that(response.item, has_entries(parameters))



def test_edit_multi_tenant():
    with fixtures.group(wazo_tenant=MAIN_TENANT) as main, fixtures.group(wazo_tenant=SUB_TENANT) as sub:
        response = confd.groups(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Group'))

        response = confd.groups(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()



def test_delete():
    with fixtures.group() as group:
        response = confd.groups(group['id']).delete()
        response.assert_deleted()
        response = confd.groups(group['id']).get()
        response.assert_match(404, e.not_found(resource='Group'))



def test_delete_multi_tenant():
    with fixtures.group(wazo_tenant=MAIN_TENANT) as main, fixtures.group(wazo_tenant=SUB_TENANT) as sub:
        response = confd.groups(main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Group'))

        response = confd.groups(sub['id']).delete(wazo_tenant=MAIN_TENANT)
        response.assert_deleted()



def test_bus_events():
    with fixtures.group() as group:
        s.check_bus_event('config.groups.created', confd.groups.post, {'name': 'group_bus_event'})
        s.check_bus_event('config.groups.edited', confd.groups(group['id']).put)
        s.check_bus_event('config.groups.deleted', confd.groups(group['id']).delete)

