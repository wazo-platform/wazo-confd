# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    not_,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd

NOT_FOUND_SWITCHBOARD_UUID = 'uuid-not-found'


def test_get_errors():
    fake_switchboard = confd.switchboards(NOT_FOUND_SWITCHBOARD_UUID).get
    s.check_resource_not_found(fake_switchboard, 'Switchboard')


def test_delete_errors():
    fake_switchboard = confd.switchboards(NOT_FOUND_SWITCHBOARD_UUID).delete
    s.check_resource_not_found(fake_switchboard, 'Switchboard')


@fixtures.moh(label='othertenant', wazo_tenant=SUB_TENANT)
def test_post_errors(_):
    switchboard_post = confd.switchboards(name='TheSwitchboard').post
    error_checks(switchboard_post)
    s.check_missing_body_returns_error(confd.switchboards, 'POST')

    s.check_bogus_field_returns_error(
        switchboard_post, 'queue_music_on_hold', 'othertenant'
    )
    s.check_bogus_field_returns_error(
        switchboard_post, 'waiting_room_music_on_hold', 'othertenant'
    )


@fixtures.switchboard()
@fixtures.moh(label='othertenant', wazo_tenant=SUB_TENANT)
def test_put_errors(switchboard, _):
    fake_switchboard = confd.switchboards(NOT_FOUND_SWITCHBOARD_UUID).put
    s.check_resource_not_found(fake_switchboard, 'Switchboard')

    url = confd.switchboards(switchboard['uuid'])
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')

    s.check_bogus_field_returns_error(url.put, 'queue_music_on_hold', 'othertenant')
    s.check_bogus_field_returns_error(
        url.put, 'waiting_room_music_on_hold', 'othertenant'
    )


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'name', 123)
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', None)
    s.check_bogus_field_returns_error(url, 'name', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'name', {})
    s.check_bogus_field_returns_error(url, 'queue_music_on_hold', 'unknown')
    s.check_bogus_field_returns_error(url, 'queue_music_on_hold', 123)
    s.check_bogus_field_returns_error(url, 'queue_music_on_hold', True)
    s.check_bogus_field_returns_error(url, 'queue_music_on_hold', False)
    s.check_bogus_field_returns_error(url, 'queue_music_on_hold', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'queue_music_on_hold', [])
    s.check_bogus_field_returns_error(url, 'queue_music_on_hold', {})
    s.check_bogus_field_returns_error(url, 'waiting_room_music_on_hold', 'unknown')
    s.check_bogus_field_returns_error(url, 'waiting_room_music_on_hold', 123)
    s.check_bogus_field_returns_error(url, 'waiting_room_music_on_hold', True)
    s.check_bogus_field_returns_error(url, 'waiting_room_music_on_hold', False)
    s.check_bogus_field_returns_error(
        url, 'waiting_room_music_on_hold', s.random_string(129)
    )
    s.check_bogus_field_returns_error(url, 'waiting_room_music_on_hold', [])
    s.check_bogus_field_returns_error(url, 'waiting_room_music_on_hold', {})
    s.check_bogus_field_returns_error(url, 'timeout', 'unknown')
    s.check_bogus_field_returns_error(url, 'timeout', True)
    s.check_bogus_field_returns_error(url, 'timeout', False)
    s.check_bogus_field_returns_error(url, 'timeout', -1)
    s.check_bogus_field_returns_error(url, 'timeout', 0)


@fixtures.switchboard(wazo_tenant=MAIN_TENANT)
@fixtures.switchboard(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.switchboards.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.switchboards.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.switchboards.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.switchboard(name='hidden', preprocess_subroutine='hidden')
@fixtures.switchboard(name='search', preprocess_subroutine='search')
def test_search(hidden, switchboard):
    url = confd.switchboards
    searches = {'name': 'search'}

    for field, term in searches.items():
        check_search(url, switchboard, hidden, field, term)


def check_search(url, switchboard, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, switchboard[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: switchboard[field]})
    assert_that(response.items, has_item(has_entry('uuid', switchboard['uuid'])))
    assert_that(response.items, is_not(has_item(has_entry('uuid', hidden['uuid']))))


@fixtures.switchboard(name='sort1')
@fixtures.switchboard(name='sort2')
def test_sorting(switchboard1, switchboard2):
    check_sorting(switchboard1, switchboard2, 'name', 'sort')


def check_sorting(switchboard1, switchboard2, field, search):
    response = confd.switchboards.get(search=search, order=field, direction='asc')
    assert_that(
        response.items,
        contains(
            has_entries(uuid=switchboard1['uuid']),
            has_entries(uuid=switchboard2['uuid']),
        ),
    )

    response = confd.switchboards.get(search=search, order=field, direction='desc')
    assert_that(
        response.items,
        contains(
            has_entries(uuid=switchboard2['uuid']),
            has_entries(uuid=switchboard1['uuid']),
        ),
    )


@fixtures.switchboard()
def test_get(switchboard):
    response = confd.switchboards(switchboard['uuid']).get()
    assert_that(
        response.item, has_entries(uuid=switchboard['uuid'], name=switchboard['name'])
    )


@fixtures.switchboard(wazo_tenant=MAIN_TENANT)
@fixtures.switchboard(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.switchboards(main['uuid']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Switchboard'))

    response = confd.switchboards(sub['uuid']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.switchboards.post(name='MySwitchboard')
    response.assert_created('switchboards')

    assert_that(
        response.item,
        has_entries(
            uuid=not_(empty()),
            queue_music_on_hold=None,
            waiting_room_music_on_hold=None,
            tenant_uuid=MAIN_TENANT,
            name='MySwitchboard',
        ),
    )

    confd.switchboards(response.item['uuid']).delete().assert_deleted()


@fixtures.moh(label='queuemoh')
@fixtures.moh(label='holdmoh')
def test_create_all_parameters(moh1, moh2):
    response = confd.switchboards.post(
        name='TheSwitchboard',
        queue_music_on_hold=moh1['name'],
        waiting_room_music_on_hold=moh2['name'],
        timeout=42,
    )
    response.assert_created('switchboards')

    assert_that(
        response.item,
        has_entries(
            uuid=not_(empty()),
            queue_music_on_hold=moh1['name'],
            waiting_room_music_on_hold=moh2['name'],
            tenant_uuid=MAIN_TENANT,
            name='TheSwitchboard',
        ),
    )

    confd.switchboards(response.item['uuid']).delete().assert_deleted()


@fixtures.switchboard(name='before_edit')
def test_edit_minimal_parameters(switchboard):
    response = confd.switchboards(switchboard['uuid']).put(name='after_edit')
    response.assert_updated()

    response = confd.switchboards(switchboard['uuid']).get()
    assert_that(response.item, has_entries(name='after_edit'))


@fixtures.moh(label='foo')
def test_update_fields_with_null_value(moh):
    response = confd.switchboards.post(
        name='TheSwitchboard',
        queue_music_on_hold=moh['name'],
        waiting_room_music_on_hold=moh['name'],
        timeout=42,
    )
    response.assert_created('switchboards')
    switchboard = response.item

    response = confd.switchboards(switchboard['uuid']).put(
        queue_music_on_hold=None,
    )
    response.assert_updated()

    response = confd.switchboards(switchboard['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            queue_music_on_hold=None,
            waiting_room_music_on_hold=moh['name'],
            timeout=42,
        ),
    )

    confd.switchboards(switchboard['uuid']).put(
        queue_music_on_hold=moh['name'],
        waiting_room_music_on_hold=moh['name'],
        timeout=42,
    )

    response = confd.switchboards(switchboard['uuid']).put(
        waiting_room_music_on_hold=None,
    )
    response.assert_updated()

    response = confd.switchboards(switchboard['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            queue_music_on_hold=moh['name'],
            waiting_room_music_on_hold=None,
            timeout=42,
        ),
    )

    confd.switchboards(switchboard['uuid']).put(
        queue_music_on_hold=moh['name'],
        waiting_room_music_on_hold=moh['name'],
        timeout=42,
    )

    response = confd.switchboards(switchboard['uuid']).put(
        timeout=None,
    )
    response.assert_updated()

    response = confd.switchboards(switchboard['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            queue_music_on_hold=moh['name'],
            waiting_room_music_on_hold=moh['name'],
            timeout=None,
        ),
    )

    confd.switchboards(response.item['uuid']).delete().assert_deleted()


@fixtures.switchboard(wazo_tenant=MAIN_TENANT)
@fixtures.switchboard(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.switchboards(main['uuid']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Switchboard'))

    response = confd.switchboards(sub['uuid']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.switchboard()
def test_delete(switchboard):
    response = confd.switchboards(switchboard['uuid']).delete()
    response.assert_deleted()
    response = confd.switchboards(switchboard['uuid']).get()
    response.assert_match(404, e.not_found(resource='Switchboard'))


@fixtures.switchboard(wazo_tenant=MAIN_TENANT)
@fixtures.switchboard(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.switchboards(main['uuid']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Switchboard'))

    response = confd.switchboards(sub['uuid']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.switchboard()
def test_bus_events(switchboard):
    url = confd.switchboards(switchboard['uuid'])
    headers = {
        'tenant_uuid': switchboard['tenant_uuid'],
    }

    s.check_event(
        'switchboard_created', headers, confd.switchboards.post, {'name': 'bus_event'}
    )
    headers['switchboard_uuid'] = switchboard['uuid']
    s.check_event('switchboard_edited', headers, url.put)
    s.check_event('switchboard_deleted', headers, url.delete)
