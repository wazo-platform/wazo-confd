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
    not_,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from ..helpers.helpers.destination import invalid_destinations, valid_destinations
from . import confd


def test_get_errors():
    fake_ivr = confd.ivr(999999).get
    s.check_resource_not_found(fake_ivr, 'IVR')


def test_delete_errors():
    fake_ivr = confd.ivr(999999).delete
    s.check_resource_not_found(fake_ivr, 'IVR')


@fixtures.user()
def test_post_errors(user):
    url = confd.ivr.post
    error_checks(url, user)


@fixtures.ivr()
@fixtures.user()
def test_put_errors(ivr, user):
    url = confd.ivr(ivr['id']).put
    error_checks(url, user)


def error_checks(url, user):
    s.check_bogus_field_returns_error(url, 'abort_sound', True)
    s.check_bogus_field_returns_error(url, 'abort_sound', 123)
    s.check_bogus_field_returns_error(url, 'abort_sound', s.random_string(256))
    s.check_bogus_field_returns_error(url, 'abort_sound', [])
    s.check_bogus_field_returns_error(url, 'abort_sound', {})
    s.check_bogus_field_returns_error(url, 'greeting_sound', True)
    s.check_bogus_field_returns_error(url, 'greeting_sound', 123)
    s.check_bogus_field_returns_error(url, 'greeting_sound', s.random_string(256))
    s.check_bogus_field_returns_error(url, 'greeting_sound', [])
    s.check_bogus_field_returns_error(url, 'greeting_sound', {})
    s.check_bogus_field_returns_error(url, 'invalid_sound', True)
    s.check_bogus_field_returns_error(url, 'invalid_sound', 123)
    s.check_bogus_field_returns_error(url, 'invalid_sound', s.random_string(256))
    s.check_bogus_field_returns_error(url, 'invalid_sound', [])
    s.check_bogus_field_returns_error(url, 'invalid_sound', {})
    s.check_bogus_field_returns_error(url, 'menu_sound', True)
    s.check_bogus_field_returns_error(url, 'menu_sound', 123)
    s.check_bogus_field_returns_error(url, 'menu_sound', s.random_string(256))
    s.check_bogus_field_returns_error(url, 'menu_sound', [])
    s.check_bogus_field_returns_error(url, 'menu_sound', {})
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', None)
    s.check_bogus_field_returns_error(url, 'name', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'name', 123)
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'name', {})
    s.check_bogus_field_returns_error(url, 'max_tries', 'invalid')
    s.check_bogus_field_returns_error(url, 'max_tries', 0)
    s.check_bogus_field_returns_error(url, 'max_tries', [])
    s.check_bogus_field_returns_error(url, 'max_tries', {})
    s.check_bogus_field_returns_error(url, 'timeout', 'invalid')
    s.check_bogus_field_returns_error(url, 'timeout', -1)
    s.check_bogus_field_returns_error(url, 'timeout', [])
    s.check_bogus_field_returns_error(url, 'timeout', {})
    s.check_bogus_field_returns_error(url, 'description', 1234)
    s.check_bogus_field_returns_error(url, 'description', [])
    s.check_bogus_field_returns_error(url, 'choices', True)
    s.check_bogus_field_returns_error(url, 'choices', 123)
    s.check_bogus_field_returns_error(url, 'choices', {})
    s.check_bogus_field_returns_error(url, 'choices', ['invalid'])
    s.check_bogus_field_returns_error(
        url, 'choices', [{'destination': {'type': 'none'}}]
    )
    s.check_bogus_field_returns_error(url, 'choices', [{'exten': '1'}])
    s.check_bogus_field_returns_error(
        url, 'choices', [{'exten': 123, 'destination': {'type': 'none'}}]
    )
    s.check_bogus_field_returns_error(
        url, 'choices', [{'exten': '1', 'destination': 'invalid'}]
    )

    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'invalid_destination', destination)
    s.check_bogus_field_returns_error(
        url,
        'invalid_destination',
        {
            'type': 'user',
            'user_id': user['id'],
            'moh_uuid': '00000000-0000-0000-0000-000000000000',
        },
        {'name': 'name', 'menu_sound': 'menu'},
        'MOH was not found',
    )

    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'timeout_destination', destination)
    s.check_bogus_field_returns_error(
        url,
        'timeout_destination',
        {
            'type': 'user',
            'user_id': user['id'],
            'moh_uuid': '00000000-0000-0000-0000-000000000000',
        },
        {'name': 'name', 'menu_sound': 'menu'},
        'MOH was not found',
    )

    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'abort_destination', destination)
    s.check_bogus_field_returns_error(
        url,
        'abort_destination',
        {
            'type': 'user',
            'user_id': user['id'],
            'moh_uuid': '00000000-0000-0000-0000-000000000000',
        },
        {'name': 'name', 'menu_sound': 'menu'},
        'MOH was not found',
    )


@fixtures.ivr(wazo_tenant=MAIN_TENANT)
@fixtures.ivr(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.ivr.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.ivr.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.ivr.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.ivr(description='search')
@fixtures.ivr(description='hidden')
def test_search(ivr, hidden):
    url = confd.ivr
    searches = {'description': 'search'}

    for field, term in searches.items():
        check_search(url, ivr, hidden, field, term)


def check_search(url, ivr, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, ivr[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: ivr[field]})
    assert_that(response.items, has_item(has_entry('id', ivr['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.ivr(description='sort1')
@fixtures.ivr(description='sort2')
def test_sorting_offset_limit(ivr1, ivr2):
    url = confd.ivr.get
    s.check_sorting(url, ivr1, ivr2, 'description', 'sort')

    s.check_offset(url, ivr1, ivr2, 'description', 'sort')
    s.check_limit(url, ivr1, ivr2, 'description', 'sort')


@fixtures.ivr()
def test_get(ivr):
    response = confd.ivr(ivr['id']).get()
    assert_that(
        response.item,
        has_entries(
            id=ivr['id'],
            name=ivr['name'],
            description=ivr['description'],
            menu_sound=ivr['menu_sound'],
            invalid_sound=ivr['invalid_sound'],
            abort_sound=ivr['abort_sound'],
            timeout=ivr['timeout'],
            max_tries=ivr['max_tries'],
            invalid_destination=ivr['invalid_destination'],
            timeout_destination=ivr['timeout_destination'],
            abort_destination=ivr['abort_destination'],
            choices=empty(),
            incalls=empty(),
        ),
    )


@fixtures.ivr(wazo_tenant=MAIN_TENANT)
@fixtures.ivr(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.ivr(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='IVR'))

    response = confd.ivr(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.ivr.post(name='ivr1', menu_sound='menu')
    response.assert_created('ivr')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, id=not_(empty())))


@fixtures.user()
@fixtures.user()
@fixtures.user()
def test_create_all_parameters(user1, user2, user3):
    response = confd.ivr.post(
        name='ivr1',
        greeting_sound='greeting',
        menu_sound='menu',
        invalid_sound='invalid',
        abort_sound='abort',
        timeout=4,
        max_tries=2,
        description='description',
        invalid_destination={'type': 'user', 'user_id': user1['id']},
        timeout_destination={'type': 'user', 'user_id': user2['id']},
        abort_destination={'type': 'user', 'user_id': user3['id']},
        choices=[{'exten': '1', 'destination': {'type': 'none'}}],
    )
    response.assert_created('ivr')

    assert_that(
        response.item,
        has_entries(
            tenant_uuid=MAIN_TENANT,
            name='ivr1',
            greeting_sound='greeting',
            menu_sound='menu',
            invalid_sound='invalid',
            abort_sound='abort',
            timeout=4,
            max_tries=2,
            description='description',
            invalid_destination=has_entries({'type': 'user', 'user_id': user1['id']}),
            timeout_destination=has_entries({'type': 'user', 'user_id': user2['id']}),
            abort_destination=has_entries({'type': 'user', 'user_id': user3['id']}),
            choices=[{'exten': '1', 'destination': {'type': 'none'}}],
        ),
    )


@fixtures.ivr(name='ivr1', menu_sound='menu')
def test_edit_minimal_parameters(ivr):
    parameters = {'name': 'ivr2', 'menu_sound': 'menu2'}

    response = confd.ivr(ivr['id']).put(**parameters)
    response.assert_updated()


@fixtures.ivr()
def test_edit_all_parameters(ivr):
    parameters = {
        'name': 'ivr1337',
        'greeting_sound': 'greeting1337',
        'menu_sound': 'menu1337',
        'invalid_sound': 'invalid1337',
        'abort_sound': 'abort1337',
        'timeout': 1337,
        'max_tries': 42,
        'description': 'leet',
        'invalid_destination': {'type': 'none'},
        'timeout_destination': {'type': 'none'},
        'abort_destination': {'type': 'none'},
        'choices': [{'exten': '0', 'destination': {'type': 'none'}}],
    }

    response = confd.ivr(ivr['id']).put(**parameters)
    response.assert_updated()

    response = confd.ivr(ivr['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.ivr()
@fixtures.ivr()
@fixtures.group()
@fixtures.outcall()
@fixtures.queue()
@fixtures.switchboard()
@fixtures.user()
@fixtures.voicemail()
@fixtures.conference()
@fixtures.skill_rule()
@fixtures.application()
@fixtures.moh()
def test_valid_destinations(ivr, *destinations):
    for destination in valid_destinations(*destinations):
        create_ivr_with_destination(destination)
        update_ivr_with_destination(ivr['id'], destination)


def create_ivr_with_destination(destination):
    response = confd.ivr.post(
        name='ivr', menu_sound='beep', abort_destination=destination
    )
    response.assert_created('ivr')
    assert_that(
        response.item, has_entries(abort_destination=has_entries(**destination))
    )


def update_ivr_with_destination(ivr_id, destination):
    response = confd.ivr(ivr_id).put(abort_destination=destination)
    response.assert_updated()
    response = confd.ivr(ivr_id).get()
    assert_that(
        response.item, has_entries(abort_destination=has_entries(**destination))
    )


@fixtures.ivr(wazo_tenant=MAIN_TENANT)
@fixtures.ivr(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.ivr(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='IVR'))

    response = confd.ivr(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.ivr()
def test_delete(ivr):
    response = confd.ivr(ivr['id']).delete()
    response.assert_deleted()
    response = confd.ivr(ivr['id']).get()
    response.assert_match(404, e.not_found(resource='IVR'))


@fixtures.ivr(wazo_tenant=MAIN_TENANT)
@fixtures.ivr(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.ivr(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='IVR'))

    response = confd.ivr(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.ivr()
def test_bus_events(ivr):
    headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event(
        'ivr_created',
        headers,
        confd.ivr.post,
        {
            'name': 'a',
            'menu_sound': 'hello',
        },
    )
    s.check_event('ivr_edited', headers, confd.ivr(ivr['id']).put)
    s.check_event('ivr_deleted', headers, confd.ivr(ivr['id']).delete)
