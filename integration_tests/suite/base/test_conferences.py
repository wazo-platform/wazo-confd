# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
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
    associations as a,
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
    gen_conference_exten,
)


def test_get_errors():
    fake_conference = confd.conferences(999999).get
    yield s.check_resource_not_found, fake_conference, 'Conference'


def test_delete_errors():
    fake_conference = confd.conferences(999999).delete
    yield s.check_resource_not_found, fake_conference, 'Conference'


def test_post_errors():
    url = confd.conferences.post
    yield from error_checks(url)


@fixtures.conference()
def test_put_errors(conference):
    url = confd.conferences(conference['id']).put
    yield from error_checks(url)


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', 1234
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', True
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', 123
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', s.random_string(
        40
    )
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', []
    yield s.check_bogus_field_returns_error, url, 'preprocess_subroutine', {}
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', 1234
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', True
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', []
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', {}
    yield s.check_bogus_field_returns_error, url, 'announce_only_user', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'announce_only_user', None
    yield s.check_bogus_field_returns_error, url, 'announce_only_user', []
    yield s.check_bogus_field_returns_error, url, 'announce_only_user', {}
    yield s.check_bogus_field_returns_error, url, 'announce_join_leave', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'announce_join_leave', None
    yield s.check_bogus_field_returns_error, url, 'announce_join_leave', []
    yield s.check_bogus_field_returns_error, url, 'announce_join_leave', {}
    yield s.check_bogus_field_returns_error, url, 'quiet_join_leave', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'quiet_join_leave', None
    yield s.check_bogus_field_returns_error, url, 'quiet_join_leave', []
    yield s.check_bogus_field_returns_error, url, 'quiet_join_leave', {}
    yield s.check_bogus_field_returns_error, url, 'announce_user_count', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'announce_user_count', None
    yield s.check_bogus_field_returns_error, url, 'announce_user_count', []
    yield s.check_bogus_field_returns_error, url, 'announce_user_count', {}
    yield s.check_bogus_field_returns_error, url, 'record', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'record', None
    yield s.check_bogus_field_returns_error, url, 'record', []
    yield s.check_bogus_field_returns_error, url, 'record', {}
    yield s.check_bogus_field_returns_error, url, 'pin', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'pin', []
    yield s.check_bogus_field_returns_error, url, 'pin', {}
    yield s.check_bogus_field_returns_error, url, 'admin_pin', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'admin_pin', []
    yield s.check_bogus_field_returns_error, url, 'admin_pin', {}


@fixtures.extension(exten=gen_conference_exten())
@fixtures.conference(name='search', preprocess_subroutine='search')
@fixtures.conference(name='hidden', preprocess_subroutine='hidden')
def test_search(extension, conference, hidden):
    url = confd.conferences
    searches = {'name': 'search', 'preprocess_subroutine': 'search'}

    for field, term in searches.items():
        yield check_search, url, conference, hidden, field, term

    searches = {'exten': extension['exten']}
    with a.conference_extension(conference, extension):
        for field, term in searches.items():
            yield check_relation_search, url, conference, hidden, field, term


def check_search(url, conference, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, conference[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: conference[field]})
    assert_that(response.items, has_item(has_entry('id', conference['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def check_relation_search(url, conference, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry('id', conference['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))

    response = url.get(**{field: term})
    assert_that(response.items, has_item(has_entry('id', conference['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.conference(wazo_tenant=MAIN_TENANT)
@fixtures.conference(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.conferences.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.conferences.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.conferences.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.conference(name='sort1')
@fixtures.conference(name='sort2')
def test_sorting_offset_limit(conference1, conference2):
    url = confd.conferences.get
    yield s.check_sorting, url, conference1, conference2, 'name', 'sort'

    yield s.check_offset, url, conference1, conference2, 'name', 'sort'
    yield s.check_limit, url, conference1, conference2, 'name', 'sort'


@fixtures.conference()
def test_get(conference):
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
        ),
    )


@fixtures.conference(wazo_tenant=MAIN_TENANT)
@fixtures.conference(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.conferences(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Conference'))

    response = confd.conferences(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.conferences.post(name='MyConference')
    response.assert_created('conferences')

    assert_that(response.item, has_entries(id=not_(empty()), tenant_uuid=MAIN_TENANT))

    confd.conferences(response.item['id']).delete().assert_deleted()


@fixtures.moh(label='music')
def test_create_all_parameters(moh):
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
        'music_on_hold': moh['name'],
    }

    response = confd.conferences.post(**parameters)
    response.assert_created('conferences')
    response = confd.conferences(response.item['id']).get()

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.conferences(response.item['id']).delete().assert_deleted()


@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_create_multi_tenant_moh(main_moh, sub_moh):
    parameters = {
        'name': 'MyConference',
        'music_on_hold': main_moh['name'],
    }
    response = confd.conferences.post(**parameters)
    response.assert_created('conferences')
    confd.conferences(response.item['id']).delete().assert_deleted()

    response = confd.conferences.post(**parameters, wazo_tenant=SUB_TENANT)
    response.assert_match(400, e.not_found(resource='MOH'))

    parameters['music_on_hold'] = sub_moh['name']

    response = confd.conferences.post(**parameters, wazo_tenant=SUB_TENANT)
    response.assert_created('conferences')
    confd.conferences(response.item['id']).delete().assert_deleted()

    response = confd.conferences.post(**parameters)
    response.assert_match(400, e.not_found(resource='MOH'))


@fixtures.conference()
def test_edit_minimal_parameters(conference):
    response = confd.conferences(conference['id']).put()
    response.assert_updated()


@fixtures.conference()
@fixtures.moh(label='music')
def test_edit_all_parameters(conference, moh):
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
        'music_on_hold': moh['name'],
    }

    response = confd.conferences(conference['id']).put(**parameters)
    response.assert_updated()

    response = confd.conferences(conference['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.conference(wazo_tenant=MAIN_TENANT)
@fixtures.conference(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.conferences(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Conference'))

    response = confd.conferences(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.conference(wazo_tenant=MAIN_TENANT)
@fixtures.conference(wazo_tenant=SUB_TENANT)
@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant_moh(main, sub, main_moh, sub_moh):
    response = confd.conferences(main['id']).put(music_on_hold=sub_moh['name'])
    response.assert_match(400, e.not_found(resource='MOH'))

    response = confd.conferences(sub['id']).put(music_on_hold=main_moh['name'])
    response.assert_match(400, e.not_found(resource='MOH'))

    response = confd.conferences(main['id']).put(music_on_hold=main_moh['name'])
    response.assert_updated()

    response = confd.conferences(sub['id']).put(music_on_hold=sub_moh['name'])
    response.assert_updated()


@fixtures.conference()
def test_dump_only_parameters(conference):
    parameters = {
        'id': 'invalid_id',
        'extensions': 'invalid_extensions',
        'incalls': 'invalid_incalls',
    }

    response = confd.conferences(conference['id']).put(**parameters)
    response.assert_updated()

    response = confd.conferences(conference['id']).get()
    assert_that(response.item, has_entries(conference))


@fixtures.conference()
def test_delete(conference):
    response = confd.conferences(conference['id']).delete()
    response.assert_deleted()
    response = confd.conferences(conference['id']).get()
    response.assert_match(404, e.not_found(resource='Conference'))


@fixtures.conference(wazo_tenant=MAIN_TENANT)
@fixtures.conference(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.conferences(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Conference'))

    response = confd.conferences(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.conference()
def test_bus_events(conference):
    headers = {'tenant_uuid': MAIN_TENANT}

    yield s.check_event, 'conference_created', headers, confd.conferences.post
    yield s.check_event, 'conference_edited', headers, confd.conferences(
        conference['id']
    ).put
    yield s.check_event, 'conference_deleted', headers, confd.conferences(
        conference['id']
    ).delete
