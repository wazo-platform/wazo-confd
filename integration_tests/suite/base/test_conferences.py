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


def test_get_errors():
    fake_conference = confd.conferences(999999).get
    s.check_resource_not_found(fake_conference, 'Conference')


def test_delete_errors():
    fake_conference = confd.conferences(999999).delete
    s.check_resource_not_found(fake_conference, 'Conference')


def test_post_errors():
    url = confd.conferences.post
    error_checks(url)


def test_put_errors():
    with fixtures.conference() as conference:
        url = confd.conferences(conference['id']).put
        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', 1234)
    s.check_bogus_field_returns_error(url, 'name', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'name', {})
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', True)
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', 123)
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', s.random_string(40))
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', [])
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', {})
    s.check_bogus_field_returns_error(url, 'music_on_hold', 1234)
    s.check_bogus_field_returns_error(url, 'music_on_hold', True)
    s.check_bogus_field_returns_error(url, 'music_on_hold', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'music_on_hold', [])
    s.check_bogus_field_returns_error(url, 'music_on_hold', {})
    s.check_bogus_field_returns_error(url, 'announce_only_user', 'invalid')
    s.check_bogus_field_returns_error(url, 'announce_only_user', None)
    s.check_bogus_field_returns_error(url, 'announce_only_user', [])
    s.check_bogus_field_returns_error(url, 'announce_only_user', {})
    s.check_bogus_field_returns_error(url, 'announce_join_leave', 'invalid')
    s.check_bogus_field_returns_error(url, 'announce_join_leave', None)
    s.check_bogus_field_returns_error(url, 'announce_join_leave', [])
    s.check_bogus_field_returns_error(url, 'announce_join_leave', {})
    s.check_bogus_field_returns_error(url, 'quiet_join_leave', 'invalid')
    s.check_bogus_field_returns_error(url, 'quiet_join_leave', None)
    s.check_bogus_field_returns_error(url, 'quiet_join_leave', [])
    s.check_bogus_field_returns_error(url, 'quiet_join_leave', {})
    s.check_bogus_field_returns_error(url, 'announce_user_count', 'invalid')
    s.check_bogus_field_returns_error(url, 'announce_user_count', None)
    s.check_bogus_field_returns_error(url, 'announce_user_count', [])
    s.check_bogus_field_returns_error(url, 'announce_user_count', {})
    s.check_bogus_field_returns_error(url, 'record', 'invalid')
    s.check_bogus_field_returns_error(url, 'record', None)
    s.check_bogus_field_returns_error(url, 'record', [])
    s.check_bogus_field_returns_error(url, 'record', {})
    s.check_bogus_field_returns_error(url, 'pin', 'invalid')
    s.check_bogus_field_returns_error(url, 'pin', [])
    s.check_bogus_field_returns_error(url, 'pin', {})
    s.check_bogus_field_returns_error(url, 'admin_pin', 'invalid')
    s.check_bogus_field_returns_error(url, 'admin_pin', [])
    s.check_bogus_field_returns_error(url, 'admin_pin', {})


def test_search():
    with fixtures.conference(name='search', preprocess_subroutine='search') as conference, fixtures.conference(name='hidden', preprocess_subroutine='hidden') as hidden:
        url = confd.conferences
        searches = {'name': 'search', 'preprocess_subroutine': 'search'}

        for field, term in searches.items():
            check_search(url, conference, hidden, field, term)



def check_search(url, conference, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, conference[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: conference[field]})
    assert_that(response.items, has_item(has_entry('id', conference['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def test_list_multi_tenant():
    with fixtures.conference(wazo_tenant=MAIN_TENANT) as main, fixtures.conference(wazo_tenant=SUB_TENANT) as sub:
        response = confd.conferences.get(wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            all_of(has_item(main)), not_(has_item(sub)),
        )

        response = confd.conferences.get(wazo_tenant=SUB_TENANT)
        assert_that(
            response.items,
            all_of(has_item(sub), not_(has_item(main))),
        )

        response = confd.conferences.get(wazo_tenant=MAIN_TENANT, recurse=True)
        assert_that(
            response.items,
            has_items(main, sub),
        )



def test_sorting_offset_limit():
    with fixtures.conference(name='sort1') as conference1, fixtures.conference(name='sort2') as conference2:
        url = confd.conferences.get
        s.check_sorting(url, conference1, conference2, 'name', 'sort')

        s.check_offset(url, conference1, conference2, 'name', 'sort')
        s.check_offset_legacy(url, conference1, conference2, 'name', 'sort')

        s.check_limit(url, conference1, conference2, 'name', 'sort')



def test_get():
    with fixtures.conference() as conference:
        response = confd.conferences(conference['id']).get()
        assert_that(
            response.item,
            has_entries(
                id=conference['id'],
                name=conference['name'],
                preprocess_subroutine=conference['preprocess_subroutine'],
                max_users=conference['max_users'],
                record=conference['record'],
                pin=conference['pin'],
                admin_pin=conference['admin_pin'],
                quiet_join_leave=conference['quiet_join_leave'],
                announce_join_leave=conference['announce_join_leave'],
                announce_user_count=conference['announce_user_count'],
                announce_only_user=conference['announce_only_user'],
                music_on_hold=conference['music_on_hold'],
                extensions=empty(),
            )
        )



def test_get_multi_tenant():
    with fixtures.conference(wazo_tenant=MAIN_TENANT) as main, fixtures.conference(wazo_tenant=SUB_TENANT) as sub:
        response = confd.conferences(main['id']).get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Conference'))

        response = confd.conferences(sub['id']).get(wazo_tenant=MAIN_TENANT)
        assert_that(response.item, has_entries(**sub))



def test_create_minimal_parameters():
    response = confd.conferences.post(name='MyConference')
    response.assert_created('conferences')

    assert_that(response.item, has_entries(id=not_(empty()), tenant_uuid=MAIN_TENANT))

    confd.conferences(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'name': 'MyConference',
        'preprocess_subroutine': 'subroutine',
        'max_users': 150,
        'record': True,
        'pin': '7654',
        'admin_pin': '7654',
        'quiet_join_leave': True,
        'announce_join_leave': True,
        'announce_user_count': True,
        'announce_only_user': False,
        'music_on_hold': 'music',
    }

    response = confd.conferences.post(**parameters)
    response.assert_created('conferences')
    response = confd.conferences(response.item['id']).get()

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.conferences(response.item['id']).delete().assert_deleted()


def test_edit_minimal_parameters():
    with fixtures.conference() as conference:
        response = confd.conferences(conference['id']).put()
        response.assert_updated()



def test_edit_all_parameters():
    with fixtures.conference() as conference:
        parameters = {
            'name': 'MyConference',
            'preprocess_subroutine': 'subroutine',
            'max_users': 150,
            'record': True,
            'pin': '7654',
            'admin_pin': '7654',
            'quiet_join_leave': True,
            'announce_join_leave': True,
            'announce_user_count': True,
            'announce_only_user': False,
            'music_on_hold': 'music',
        }

        response = confd.conferences(conference['id']).put(**parameters)
        response.assert_updated()

        response = confd.conferences(conference['id']).get()
        assert_that(response.item, has_entries(parameters))



def test_edit_multi_tenant():
    with fixtures.conference(wazo_tenant=MAIN_TENANT) as main, fixtures.conference(wazo_tenant=SUB_TENANT) as sub:
        response = confd.conferences(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Conference'))

        response = confd.conferences(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()



def test_dump_only_parameters():
    with fixtures.conference() as conference:
        parameters = {
            'id': 'invalid_id',
            'extensions': 'invalid_extensions',
            'incalls': 'invalid_incalls',
        }

        response = confd.conferences(conference['id']).put(**parameters)
        response.assert_updated()

        response = confd.conferences(conference['id']).get()
        assert_that(response.item, has_entries(conference))



def test_delete():
    with fixtures.conference() as conference:
        response = confd.conferences(conference['id']).delete()
        response.assert_deleted()
        response = confd.conferences(conference['id']).get()
        response.assert_match(404, e.not_found(resource='Conference'))



def test_delete_multi_tenant():
    with fixtures.conference(wazo_tenant=MAIN_TENANT) as main, fixtures.conference(wazo_tenant=SUB_TENANT) as sub:
        response = confd.conferences(main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Conference'))

        response = confd.conferences(sub['id']).delete(wazo_tenant=MAIN_TENANT)
        response.assert_deleted()



def test_bus_events():
    with fixtures.conference() as conference:
        s.check_bus_event('config.conferences.created', confd.conferences.post)
        s.check_bus_event('config.conferences.edited', confd.conferences(conference['id']).put)
        s.check_bus_event('config.conferences.deleted', confd.conferences(conference['id']).delete)

