# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
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

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import EXTEN_GROUP_RANGE, MAIN_TENANT, SUB_TENANT
from . import confd


def test_get_errors():
    fake_group = confd.groups(999999).get
    s.check_resource_not_found(fake_group, 'Group')


def test_delete_errors():
    fake_group = confd.groups(999999).delete
    s.check_resource_not_found(fake_group, 'Group')


def test_post_errors():
    url = confd.groups.post
    error_checks(url)


@fixtures.group()
def test_put_errors(group):
    url = confd.groups(group['id']).put
    error_checks(url)

    url = confd.groups(group['uuid']).put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'label', 123)
    s.check_bogus_field_returns_error(url, 'label', True)
    s.check_bogus_field_returns_error(url, 'label', None)
    s.check_bogus_field_returns_error(url, 'label', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'label', 'legitimate name\nconfig injection')
    s.check_bogus_field_returns_error(url, 'label', [])
    s.check_bogus_field_returns_error(url, 'label', {})
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', 123)
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', s.random_string(80))
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
    s.check_bogus_field_returns_error(url, 'dtmf_record_toggle', 'yeah')
    s.check_bogus_field_returns_error(url, 'dtmf_record_toggle', 123)
    s.check_bogus_field_returns_error(url, 'dtmf_record_toggle', {})
    s.check_bogus_field_returns_error(url, 'dtmf_record_toggle', [])
    s.check_bogus_field_returns_error(url, 'ignore_forward', 'yeah')
    s.check_bogus_field_returns_error(url, 'ignore_forward', 123)
    s.check_bogus_field_returns_error(url, 'ignore_forward', {})
    s.check_bogus_field_returns_error(url, 'ignore_forward', [])
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
    s.check_bogus_field_returns_error(url, 'mark_answered_elsewhere', 'yeah')
    s.check_bogus_field_returns_error(url, 'mark_answered_elsewhere', 123)
    s.check_bogus_field_returns_error(url, 'mark_answered_elsewhere', {})
    s.check_bogus_field_returns_error(url, 'mark_answered_elsewhere', [])
    s.check_bogus_field_returns_error(url, 'enabled', 'yeah')
    s.check_bogus_field_returns_error(url, 'enabled', 123)
    s.check_bogus_field_returns_error(url, 'enabled', {})
    s.check_bogus_field_returns_error(url, 'enabled', [])
    s.check_bogus_field_returns_error(url, 'max_calls', 'ten')
    s.check_bogus_field_returns_error(url, 'max_calls', -1)
    s.check_bogus_field_returns_error(url, 'max_calls', {})
    s.check_bogus_field_returns_error(url, 'max_calls', [])


@fixtures.extension(exten_range=EXTEN_GROUP_RANGE)
@fixtures.group(label='hidden', preprocess_subroutine='hidden')
@fixtures.group(label='search', preprocess_subroutine='search')
def test_search(extension, hidden, group):
    url = confd.groups
    searches = {'label': 'search', 'preprocess_subroutine': 'search'}

    for field, term in searches.items():
        check_search(url, group, hidden, field, term)

    searches = {'exten': extension['exten']}
    with a.group_extension(group, extension):
        for field, term in searches.items():
            check_relation_search(url, group, hidden, field, term)


def check_search(url, group, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, group[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: group[field]})
    assert_that(response.items, has_item(has_entry('uuid', group['uuid'])))
    assert_that(response.items, is_not(has_item(has_entry('uuid', hidden['uuid']))))


def check_relation_search(url, group, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry('uuid', group['uuid'])))
    assert_that(response.items, is_not(has_item(has_entry('uuid', hidden['uuid']))))

    response = url.get(**{field: term})
    assert_that(response.items, has_item(has_entry('uuid', group['uuid'])))
    assert_that(response.items, is_not(has_item(has_entry('uuid', hidden['uuid']))))


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.groups.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.groups.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.groups.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.group(label='sort1', preprocess_subroutine='sort1')
@fixtures.group(label='sort2', preprocess_subroutine='sort2')
def test_sorting_offset_limit(group1, group2):
    url = confd.groups.get
    s.check_sorting(url, group1, group2, 'label', 'sort')
    s.check_sorting(url, group1, group2, 'preprocess_subroutine', 'sort')

    s.check_offset(url, group1, group2, 'label', 'sort')
    s.check_limit(url, group1, group2, 'label', 'sort')


@fixtures.group()
def test_get(group):
    response = confd.groups(group['id']).get()
    assert_that(
        response.item,
        has_entries(
            id=group['id'],
            uuid=group['uuid'],
            name=group['name'],
            label=group['label'],
            caller_id_mode=group['caller_id_mode'],
            caller_id_name=group['caller_id_name'],
            dtmf_record_toggle=group['dtmf_record_toggle'],
            timeout=group['timeout'],
            music_on_hold=group['music_on_hold'],
            preprocess_subroutine=group['preprocess_subroutine'],
            ring_in_use=group['ring_in_use'],
            ring_strategy=group['ring_strategy'],
            user_timeout=group['user_timeout'],
            retry_delay=group['retry_delay'],
            mark_answered_elsewhere=group['mark_answered_elsewhere'],
            enabled=group['enabled'],
            max_calls=group['max_calls'],
            extensions=empty(),
            members=has_entries(users=empty(), extensions=empty()),
            incalls=empty(),
            fallbacks=has_entries(noanswer_destination=none()),
            ignore_forward=group['ignore_forward'],
        ),
    )

    response = confd.groups(group['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            id=group['id'],
            uuid=group['uuid'],
            name=group['name'],
            label=group['label'],
            caller_id_mode=group['caller_id_mode'],
            caller_id_name=group['caller_id_name'],
            dtmf_record_toggle=group['dtmf_record_toggle'],
            timeout=group['timeout'],
            music_on_hold=group['music_on_hold'],
            preprocess_subroutine=group['preprocess_subroutine'],
            ring_in_use=group['ring_in_use'],
            ring_strategy=group['ring_strategy'],
            user_timeout=group['user_timeout'],
            retry_delay=group['retry_delay'],
            mark_answered_elsewhere=group['mark_answered_elsewhere'],
            enabled=group['enabled'],
            max_calls=group['max_calls'],
            extensions=empty(),
            members=has_entries(users=empty(), extensions=empty()),
            incalls=empty(),
            fallbacks=has_entries(noanswer_destination=none()),
            ignore_forward=group['ignore_forward'],
        ),
    )


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.groups(main['uuid']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Group'))

    response = confd.groups(sub['uuid']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))

    response = confd.groups(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Group'))

    response = confd.groups(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.groups.post(label='MyGroup')
    response.assert_created('groups')

    assert_that(
        response.item,
        has_entries(
            id=not_(empty()),
            name=not_(empty()),
            label='MyGroup',
            tenant_uuid=MAIN_TENANT,
        ),
    )

    confd.groups(response.item['id']).delete().assert_deleted()

    response = confd.groups.post(label='MyGroup')
    response.assert_created('groups')

    assert_that(
        response.item,
        has_entries(
            uuid=not_(empty()),
            name=not_(empty()),
            label='MyGroup',
            tenant_uuid=MAIN_TENANT,
        ),
    )

    confd.groups(response.item['uuid']).delete().assert_deleted()


def test_create_deprecated_name():
    response = confd.groups.post(name='MyGroup')
    response.assert_created('groups')

    assert_that(
        response.item,
        has_entries(
            uuid=not_(empty()),
            name=not_(empty()),
            label='MyGroup',
        ),
    )

    confd.groups(response.item['uuid']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'label': 'MyGroup',
        'caller_id_mode': 'prepend',
        'caller_id_name': 'GROUP-',
        'dtmf_record_toggle': True,
        'timeout': 42,
        'music_on_hold': 'default',
        'preprocess_subroutine': 'subroutien',
        'ring_in_use': False,
        'ring_strategy': 'weight_random',
        'mark_answered_elsewhere': False,
        'user_timeout': 24,
        'retry_delay': 12,
        'enabled': False,
        'max_calls': 42,
        'ignore_forward': False,
    }

    response = confd.groups.post(**parameters)
    response.assert_created('groups')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.groups(response.item['uuid']).delete().assert_deleted()


def test_create_multi_tenant():
    response = confd.groups.post(label='MyGroup', wazo_tenant=SUB_TENANT)
    response.assert_created('groups')

    assert_that(response.item, has_entries(tenant_uuid=SUB_TENANT))

    confd.groups(response.item['uuid']).delete().assert_deleted()


@fixtures.moh(label='visible')
@fixtures.moh(label='hidden', wazo_tenant=SUB_TENANT)
def test_create_multi_tenant_moh(moh_main, moh_sub):
    response = confd.groups.post(label='MyGroup', music_on_hold=moh_main['name'])
    response.assert_created('groups')
    confd.groups(response.item['uuid']).delete().assert_deleted()

    response = confd.groups.post(label='MyGroup', music_on_hold=moh_sub['name'])
    response.assert_match(400, e.not_found(resource='MOH'))

    response = confd.groups.post(
        label='MyGroup',
        music_on_hold=moh_main['name'],
        wazo_tenant=SUB_TENANT,
    )
    response.assert_match(400, e.not_found(resource='MOH'))


@fixtures.group()
def test_edit_minimal_parameters(group):
    response = confd.groups(group['id']).put()
    response.assert_updated()

    response = confd.groups(group['uuid']).put()
    response.assert_updated()


@fixtures.group()
def test_edit_all_parameters(group):
    parameters = {
        'name': 'ignored',
        'label': 'MyGroup',
        'caller_id_mode': 'prepend',
        'caller_id_name': 'GROUP-',
        'dtmf_record_toggle': True,
        'timeout': 42,
        'music_on_hold': 'default',
        'preprocess_subroutine': 'subroutien',
        'ring_in_use': False,
        'ring_strategy': 'random',
        'mark_answered_elsewhere': False,
        'user_timeout': 24,
        'retry_delay': 12,
        'enabled': False,
        'max_calls': 42,
        'ignore_forward': False,
    }

    response = confd.groups(group['id']).put(**parameters)
    response.assert_updated()

    response = confd.groups(group['id']).get()
    expected = dict(parameters)
    expected['name'] = group['name']
    assert_that(response.item, has_entries(expected))

    parameters = {
        'name': 'ignored2',
        'label': 'MyGroup2',
        'caller_id_mode': 'prepend',
        'caller_id_name': 'GROUP2-',
        'dtmf_record_toggle': False,
        'timeout': 43,
        'music_on_hold': 'default',
        'preprocess_subroutine': 'subroutien2',
        'ring_in_use': False,
        'ring_strategy': 'random',
        'mark_answered_elsewhere': False,
        'user_timeout': 24,
        'retry_delay': 12,
        'enabled': False,
        'max_calls': 0,
        'ignore_forward': True,
    }

    response = confd.groups(group['uuid']).put(**parameters)
    response.assert_updated()

    expected = dict(parameters)
    expected['name'] = group['name']
    response = confd.groups(group['uuid']).get()
    assert_that(response.item, has_entries(expected))


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.groups(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Group'))

    response = confd.groups(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()

    response = confd.groups(main['uuid']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Group'))

    response = confd.groups(sub['uuid']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant_moh(main_group, sub_group, main_moh, sub_moh):
    response = confd.groups(main_group['id']).put(music_on_hold=main_moh['name'])
    response.assert_updated()

    response = confd.groups(sub_group['id']).put(music_on_hold=sub_moh['name'])
    response.assert_updated()

    response = confd.groups(main_group['id']).put(music_on_hold=sub_moh['name'])
    response.assert_match(400, e.not_found(resource='MOH'))

    response = confd.groups(sub_group['id']).put(music_on_hold=main_moh['name'])
    response.assert_match(400, e.not_found(resource='MOH'))


@fixtures.group()
@fixtures.group()
def test_delete(group_1, group_2):
    response = confd.groups(group_1['id']).delete()
    response.assert_deleted()
    response = confd.groups(group_1['id']).get()
    response.assert_match(404, e.not_found(resource='Group'))

    response = confd.groups(group_2['uuid']).delete()
    response.assert_deleted()
    response = confd.groups(group_2['uuid']).get()
    response.assert_match(404, e.not_found(resource='Group'))


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.groups(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Group'))

    response = confd.groups(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant_by_uuid(main, sub):
    response = confd.groups(main['uuid']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Group'))

    response = confd.groups(sub['uuid']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.group()
def test_bus_events(group):
    headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event(
        'group_created', headers, confd.groups.post, {'label': 'group_bus_event'}
    )
    s.check_event('group_edited', headers, confd.groups(group['id']).put)
    s.check_event('group_deleted', headers, confd.groups(group['id']).delete)


@fixtures.group()
def test_bus_events_by_uuid(group):
    headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event(
        'group_created',
        headers,
        confd.groups.post,
        {'label': 'group_bus_event_with_uuid'},
    )
    s.check_event('group_edited', headers, confd.groups(group['uuid']).put)
    s.check_event('group_deleted', headers, confd.groups(group['uuid']).delete)
