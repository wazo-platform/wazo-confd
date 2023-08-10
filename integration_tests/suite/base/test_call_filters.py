# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
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
from ..helpers import errors as e, fixtures, scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT


def test_get_errors():
    fake_get = confd.callfilters(999999).get
    yield s.check_resource_not_found, fake_get, 'CallFilter'


def test_post_errors():
    url = confd.callfilters.post
    for check in error_checks(url):
        yield check


@fixtures.call_filter()
def test_put_errors(call_filter):
    url = confd.callfilters(call_filter['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'label', 123
    yield s.check_bogus_field_returns_error, url, 'label', None
    yield s.check_bogus_field_returns_error, url, 'label', True
    yield s.check_bogus_field_returns_error, url, 'label', {}
    yield s.check_bogus_field_returns_error, url, 'label', []
    yield s.check_bogus_field_returns_error, url, 'label', 'a' * 129
    yield s.check_bogus_field_returns_error, url, 'name', 123, None, 'label'
    yield s.check_bogus_field_returns_error, url, 'name', None, None, 'label'
    yield s.check_bogus_field_returns_error, url, 'name', True, None, 'label'
    yield s.check_bogus_field_returns_error, url, 'name', {}, None, 'label'
    yield s.check_bogus_field_returns_error, url, 'name', [], None, 'label'
    yield s.check_bogus_field_returns_error, url, 'name', 'a' * 129, None, 'label'
    yield s.check_bogus_field_returns_error, url, 'source', 123
    yield s.check_bogus_field_returns_error, url, 'source', True
    yield s.check_bogus_field_returns_error, url, 'source', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'source', {}
    yield s.check_bogus_field_returns_error, url, 'source', []
    yield s.check_bogus_field_returns_error, url, 'strategy', 123
    yield s.check_bogus_field_returns_error, url, 'strategy', None
    yield s.check_bogus_field_returns_error, url, 'strategy', False
    yield s.check_bogus_field_returns_error, url, 'strategy', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'strategy', {}
    yield s.check_bogus_field_returns_error, url, 'strategy', []
    yield s.check_bogus_field_returns_error, url, 'surrogates_timeout', 'ten'
    yield s.check_bogus_field_returns_error, url, 'surrogates_timeout', -1
    yield s.check_bogus_field_returns_error, url, 'surrogates_timeout', {}
    yield s.check_bogus_field_returns_error, url, 'surrogates_timeout', []
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', True
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', 1234
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id_mode', []
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', 1234
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', True
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', s.random_string(81)
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', {}
    yield s.check_bogus_field_returns_error, url, 'caller_id_name', []
    yield s.check_bogus_field_returns_error, url, 'description', 123
    yield s.check_bogus_field_returns_error, url, 'description', True
    yield s.check_bogus_field_returns_error, url, 'description', {}
    yield s.check_bogus_field_returns_error, url, 'description', []
    yield s.check_bogus_field_returns_error, url, 'enabled', None
    yield s.check_bogus_field_returns_error, url, 'enabled', 123
    yield s.check_bogus_field_returns_error, url, 'enabled', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'enabled', {}
    yield s.check_bogus_field_returns_error, url, 'enabled', []


@fixtures.call_filter(label="search", description="SearchDesc")
@fixtures.call_filter(label="hidden", description="HiddenDesc")
def test_search(call_filter, hidden):
    url = confd.callfilters
    searches = {'label': 'search', 'description': 'Search'}

    for field, term in searches.items():
        yield check_search, url, call_filter, hidden, field, term


def check_search(url, call_filter, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, call_filter[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: call_filter[field]})
    assert_that(response.items, has_item(has_entry('id', call_filter['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.call_filter(label="sort1", description="Sort 1")
@fixtures.call_filter(label="sort2", description="Sort 2")
def test_sorting_offset_limit(call_filter1, call_filter2):
    url = confd.callfilters.get
    yield s.check_sorting, url, call_filter1, call_filter2, 'label', 'sort'
    yield s.check_sorting, url, call_filter1, call_filter2, 'description', 'Sort'

    yield s.check_offset, url, call_filter1, call_filter2, 'label', 'sort'
    yield s.check_limit, url, call_filter1, call_filter2, 'label', 'sort'


@fixtures.call_filter(wazo_tenant=MAIN_TENANT)
@fixtures.call_filter(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.callfilters.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.callfilters.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.callfilters.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.call_filter()
def test_get(call_filter):
    response = confd.callfilters(call_filter['id']).get()
    assert_that(
        response.item,
        has_entries(
            name=call_filter['name'],
            label=call_filter['label'],
            source=call_filter['source'],
            caller_id_mode=none(),
            caller_id_name=none(),
            strategy=call_filter['strategy'],
            surrogates_timeout=none(),
            description=none(),
            enabled=True,
            recipients=has_entries(users=empty()),
            surrogates=has_entries(users=empty()),
            fallbacks=has_entries(noanswer_destination=none()),
        ),
    )


@fixtures.call_filter(wazo_tenant=MAIN_TENANT)
@fixtures.call_filter(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.callfilters(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='CallFilter'))

    response = confd.callfilters(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.callfilters.post(label='minimal', source='all', strategy='all')
    response.assert_created('callfilters')

    assert_that(response.item, has_entries(id=not_(empty()), tenant_uuid=MAIN_TENANT))

    confd.callfilters(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'label': 'all parameters',
        'source': 'all',
        'strategy': 'all',
        'surrogates_timeout': 10,
        'caller_id_mode': 'prepend',
        'caller_id_name': 'callidname',
        'description': 'Create description',
        'enabled': False,
    }

    response = confd.callfilters.post(**parameters)
    response.assert_created('callfilters')
    assert_that(
        response.item,
        has_entries(
            tenant_uuid=MAIN_TENANT,
            name=not_(empty()),
            label='all parameters',
            source='all',
            strategy='all',
            surrogates_timeout=10,
            caller_id_mode='prepend',
            caller_id_name='callidname',
            description='Create description',
            enabled=False,
        ),
    )
    confd.callfilters(response.item['id']).delete().assert_deleted()


@fixtures.call_filter(strategy='all-recipients-then-linear-surrogates')
@fixtures.call_filter(strategy='all-recipients-then-all-surrogates')
@fixtures.call_filter(strategy='all-surrogates-then-all-recipients')
@fixtures.call_filter(strategy='linear-surrogates-then-all-recipients')
@fixtures.call_filter(strategy='all')
@fixtures.call_filter(source='external')
@fixtures.call_filter(source='internal')
@fixtures.call_filter(source='all')
@fixtures.call_filter(caller_id_mode='prepend')
@fixtures.call_filter(caller_id_mode='append')
@fixtures.call_filter(caller_id_mode='overwrite')
def test_create_with_every_enum(self, *call_filters):
    pass


def test_create_without_label():
    response = confd.callfilters.post()
    response.assert_status(400)


def test_create_with_name_copied_into_label():
    response = confd.callfilters.post(
        name='test-to-label', source='all', strategy='all'
    )
    response.assert_created('callfilters')
    assert_that(
        response.item,
        has_entries(
            name=is_not('test-to-label'),
            label='test-to-label',
        ),
    )
    confd.callfilters(response.item['id']).delete().assert_deleted()


@fixtures.call_filter()
def test_edit_minimal_parameters(call_filter):
    response = confd.callfilters(call_filter['id']).put()
    response.assert_updated()


@fixtures.call_filter()
def test_edit_all_parameters(call_filter):
    parameters = {
        'label': 'edit label',
        'source': 'all',
        'strategy': 'all',
        'surrogates_timeout': 10,
        'caller_id_mode': 'prepend',
        'caller_id_name': 'callidname',
        'description': 'Create description',
        'enabled': False,
    }

    response = confd.callfilters(call_filter['id']).put(**parameters)
    response.assert_updated()

    response = confd.callfilters(call_filter['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.call_filter(wazo_tenant=MAIN_TENANT)
@fixtures.call_filter(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.callfilters(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='CallFilter'))

    response = confd.callfilters(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.call_filter()
def test_delete(call_filter):
    response = confd.callfilters(call_filter['id']).delete()
    response.assert_deleted()
    confd.callfilters(call_filter['id']).get().assert_status(404)


@fixtures.call_filter(wazo_tenant=MAIN_TENANT)
@fixtures.call_filter(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.callfilters(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='CallFilter'))

    response = confd.callfilters(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()
