# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
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
from ..helpers import errors as e, fixtures, scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT

FAKE_UUID = '99999999-9999-4999-9999-999999999999'


def test_get_errors():
    fake_get = confd.meetings(FAKE_UUID).get
    yield s.check_resource_not_found, fake_get, 'Meeting'


def test_post_errors():
    url = confd.meetings.post
    for check in error_checks(url):
        yield check


@fixtures.meeting()
def test_put_errors(meeting):
    url = confd.meetings(meeting['uuid']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', 'a' * 513


@fixtures.meeting(wazo_tenant=MAIN_TENANT)
@fixtures.meeting(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.meetings.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.meetings.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.meetings.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.meeting(name="search")
@fixtures.meeting(name="hidden")
def test_search(meeting, hidden):
    url = confd.meetings
    searches = {'name': 'search'}

    for field, term in searches.items():
        yield check_search, url, meeting, hidden, field, term


def check_search(url, meeting, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, meeting[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: meeting[field]})

    assert_that(response.items, has_item(has_entry('uuid', meeting['uuid'])))
    assert_that(response.items, is_not(has_item(has_entry('uuid', hidden['uuid']))))


@fixtures.meeting(name="sort1")
@fixtures.meeting(name="sort2")
def test_sorting_offset_limit(meeting1, meeting2):
    url = confd.meetings.get
    yield s.check_sorting, url, meeting1, meeting2, 'name', 'sort', 'uuid'

    yield s.check_offset, url, meeting1, meeting2, 'name', 'sort', 'uuid'
    yield s.check_limit, url, meeting1, meeting2, 'name', 'sort', 'uuid'


@fixtures.meeting()
def test_get(meeting):
    response = confd.meetings(meeting['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            name=meeting['name'],
        ),
    )


@fixtures.meeting(wazo_tenant=MAIN_TENANT)
@fixtures.meeting(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.meetings(main['uuid']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Meeting'))

    response = confd.meetings(sub['uuid']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.meetings.post(name='minimal')
    response.assert_created('meetings')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, uuid=not_(empty())))

    confd.meetings(response.item['uuid']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {'name': 'allparameter'}

    response = confd.meetings.post(**parameters)
    response.assert_created('meetings')
    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))
    confd.meetings(response.item['uuid']).delete().assert_deleted()


def test_create_without_name():
    response = confd.meetings.post()
    response.assert_status(400)


@fixtures.meeting()
def test_edit_minimal_parameters(meeting):
    response = confd.meetings(meeting['uuid']).put()
    response.assert_updated()


@fixtures.meeting()
def test_edit_all_parameters(meeting):
    parameters = {'name': 'editallparameter'}

    response = confd.meetings(meeting['uuid']).put(**parameters)
    response.assert_updated()

    response = confd.meetings(meeting['uuid']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.meeting(wazo_tenant=MAIN_TENANT)
@fixtures.meeting(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.meetings(main['uuid']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Meeting'))

    response = confd.meetings(sub['uuid']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.meeting()
def test_delete(meeting):
    response = confd.meetings(meeting['uuid']).delete()
    response.assert_deleted()
    confd.meetings(meeting['uuid']).get().assert_status(404)


@fixtures.meeting(wazo_tenant=MAIN_TENANT)
@fixtures.meeting(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.meetings(main['uuid']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Meeting'))

    response = confd.meetings(sub['uuid']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.meeting()
def test_bus_events(meeting):
    yield s.check_bus_event, 'config.meetings.created', confd.meetings.post, {
        'name': 'meeting'
    }
    yield s.check_bus_event, 'config.meetings.updated', confd.meetings(
        meeting['uuid']
    ).put
    yield s.check_bus_event, 'config.meetings.deleted', confd.meetings(
        meeting['uuid']
    ).delete
