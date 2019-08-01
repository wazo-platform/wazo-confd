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
from ..helpers.helpers.destination import invalid_destinations, valid_destinations


def test_get_errors():
    fake_ivr = confd.ivr(999999).get
    s.check_resource_not_found(fake_ivr, 'IVR')


def test_delete_errors():
    fake_ivr = confd.ivr(999999).delete
    s.check_resource_not_found(fake_ivr, 'IVR')


def test_post_errors():
    url = confd.ivr.post
    error_checks(url)


def test_put_errors():
    with fixtures.ivr() as ivr:
        url = confd.ivr(ivr['id']).put
        error_checks(url)



def error_checks(url):
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
    s.check_bogus_field_returns_error(url, 'choices', [{'destination': {'type': 'none'}}])
    s.check_bogus_field_returns_error(url, 'choices', [{'exten': '1'}])
    s.check_bogus_field_returns_error(url, 'choices', [{'exten': 123, 'destination': {'type': 'none'}}])
    s.check_bogus_field_returns_error(url, 'choices', [{'exten': '1', 'destination': 'invalid'}])

    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'invalid_destination', destination)
    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'timeout_destination', destination)
    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'abort_destination', destination)


def test_list_multi_tenant():
    with fixtures.ivr(wazo_tenant=MAIN_TENANT) as main, fixtures.ivr(wazo_tenant=SUB_TENANT) as sub:
        response = confd.ivr.get(wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            all_of(has_item(main)), not_(has_item(sub)),
        )

        response = confd.ivr.get(wazo_tenant=SUB_TENANT)
        assert_that(
            response.items,
            all_of(has_item(sub), not_(has_item(main))),
        )

        response = confd.ivr.get(wazo_tenant=MAIN_TENANT, recurse=True)
        assert_that(
            response.items,
            has_items(main, sub),
        )



def test_search():
    with fixtures.ivr(description='search') as ivr, fixtures.ivr(description='hidden') as hidden:
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


def test_sorting_offset_limit():
    with fixtures.ivr(description='sort1') as ivr1, fixtures.ivr(description='sort2') as ivr2:
        url = confd.ivr.get
        s.check_sorting(url, ivr1, ivr2, 'description', 'sort')

        s.check_offset(url, ivr1, ivr2, 'description', 'sort')
        s.check_offset_legacy(url, ivr1, ivr2, 'description', 'sort')

        s.check_limit(url, ivr1, ivr2, 'description', 'sort')



def test_get():
    with fixtures.ivr() as ivr:
        response = confd.ivr(ivr['id']).get()
        assert_that(response.item, has_entries(
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
        ))



def test_get_multi_tenant():
    with fixtures.ivr(wazo_tenant=MAIN_TENANT) as main, fixtures.ivr(wazo_tenant=SUB_TENANT) as sub:
        response = confd.ivr(main['id']).get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='IVR'))

        response = confd.ivr(sub['id']).get(wazo_tenant=MAIN_TENANT)
        assert_that(response.item, has_entries(**sub))



def test_create_minimal_parameters():
    response = confd.ivr.post(name='ivr1', menu_sound='menu')
    response.assert_created('ivr')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, id=not_(empty())))


def test_create_all_parameters():
    with fixtures.user() as user1, fixtures.user() as user2, fixtures.user() as user3:
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

        assert_that(response.item, has_entries(
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
        ))



def test_edit_minimal_parameters():
    with fixtures.ivr(name='ivr1', menu_sound='menu') as ivr:
        parameters = {'name': 'ivr2', 'menu_sound': 'menu2'}

        response = confd.ivr(ivr['id']).put(**parameters)
        response.assert_updated()



def test_edit_all_parameters():
    with fixtures.ivr() as ivr:
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



def test_valid_destinations():
    with fixtures.ivr() as ivr, \
            fixtures.meetme() as meetme, \
            fixtures.ivr() as ivr2, \
            fixtures.group() as group, \
            fixtures.outcall() as outcall, \
            fixtures.queue() as queue, \
            fixtures.switchboard() as switchboard, \
            fixtures.user() as user, \
            fixtures.voicemail() as voicemail, \
            fixtures.conference() as conference, \
            fixtures.skill_rule() as skill_rule, \
            fixtures.application() as application:

        destinations = (meetme, ivr2, group, outcall, queue, switchboard,
                        user, voicemail, conference, skill_rule, application)

        for destination in valid_destinations(*destinations):
            create_ivr_with_destination(destination)
            update_ivr_with_destination(ivr['id'], destination)


def create_ivr_with_destination(destination):
    response = confd.ivr.post(name='ivr', menu_sound='beep', abort_destination=destination)
    response.assert_created('ivr')
    assert_that(response.item, has_entries(abort_destination=has_entries(**destination)))


def update_ivr_with_destination(ivr_id, destination):
    response = confd.ivr(ivr_id).put(abort_destination=destination)
    response.assert_updated()
    response = confd.ivr(ivr_id).get()
    assert_that(response.item, has_entries(abort_destination=has_entries(**destination)))


def test_edit_multi_tenant():
    with fixtures.ivr(wazo_tenant=MAIN_TENANT) as main, fixtures.ivr(wazo_tenant=SUB_TENANT) as sub:
        response = confd.ivr(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='IVR'))

        response = confd.ivr(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()



def test_delete():
    with fixtures.ivr() as ivr:
        response = confd.ivr(ivr['id']).delete()
        response.assert_deleted()
        response = confd.ivr(ivr['id']).get()
        response.assert_match(404, e.not_found(resource='IVR'))



def test_delete_multi_tenant():
    with fixtures.ivr(wazo_tenant=MAIN_TENANT) as main, fixtures.ivr(wazo_tenant=SUB_TENANT) as sub:
        response = confd.ivr(main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='IVR'))

        response = confd.ivr(sub['id']).delete(wazo_tenant=MAIN_TENANT)
        response.assert_deleted()



def test_bus_events():
    with fixtures.ivr() as ivr:
        s.check_bus_event('config.ivr.created', confd.ivr.post, {'name': 'a', 'menu_sound': 'hello'})
        s.check_bus_event('config.ivr.edited', confd.ivr(ivr['id']).put)
        s.check_bus_event('config.ivr.deleted', confd.ivr(ivr['id']).delete)

