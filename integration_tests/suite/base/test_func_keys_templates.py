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
    none,
    not_,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd
from .test_func_keys import error_funckey_checks, error_funckeys_checks

invalid_template_destinations = [
    {'type': 'agent'},
    {'type': 'agent', 'agent_id': 1234},
    {'type': 'bsfilter'},
    {'type': 'bsfilter', 'filter_member_id': 1234},
]


def test_get_errors():
    fake_get = confd.funckeys.templates(999999).get
    s.check_resource_not_found(fake_get, 'FuncKeyTemplate')


def test_post_errors():
    url = confd.funckeys.templates.post
    error_funckeys_checks(url)

    regex = r'keys.*1.*destination.*type'
    for destination in invalid_template_destinations:
        s.check_bogus_field_returns_error_matching_regex(
            url, 'keys', {'1': {'destination': destination}}, regex
        )


@fixtures.funckey_template()
def test_get_position_errors(funckey_template):
    fake_get = confd.funckeys.templates(funckey_template['id'])(1).get
    s.check_resource_not_found(fake_get, 'FuncKey')


# Should raise an error
# @fixtures.funckey_template()
# def test_delete_position_errors(funckey_template):
#     fake_delete = confd.funckeys.templates(funckey_template['id'])(1).delete
#     s.check_resource_not_found(fake_delete, 'FuncKey')


@fixtures.funckey_template()
def test_put_position_errors(funckey_template):
    url = confd.funckeys.templates(funckey_template['id'])(1).put
    error_funckey_checks(url)

    for destination in invalid_template_destinations:
        s.check_bogus_field_returns_error(url, 'destination', destination)


@fixtures.funckey_template(name="search")
@fixtures.funckey_template(name="hidden")
def test_search_on_funckey_template(funckey_template, hidden):
    url = confd.funckeys.templates
    searches = {'name': 'search'}

    for field, term in searches.items():
        check_search(url, funckey_template, hidden, field, term)


def check_search(url, funckey_template, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, funckey_template[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))


@fixtures.funckey_template(name='sort1')
@fixtures.funckey_template(name='sort2')
def test_funckey_template_sorting(funckey_template1, funckey_template2):
    check_funckey_template_sorting(funckey_template1, funckey_template2, 'name', 'sort')


def check_funckey_template_sorting(funckey_template1, funckey_template2, field, search):
    response = confd.funckeys.templates.get(search=search, order=field, direction='asc')
    assert_that(
        response.items,
        contains(
            has_entries(id=funckey_template1['id']),
            has_entries(id=funckey_template2['id']),
        ),
    )

    response = confd.funckeys.templates.get(
        search=search, order=field, direction='desc'
    )
    assert_that(
        response.items,
        contains(
            has_entries(id=funckey_template2['id']),
            has_entries(id=funckey_template1['id']),
        ),
    )


@fixtures.funckey_template(wazo_tenant=MAIN_TENANT)
@fixtures.funckey_template(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.funckeys.templates.get(wazo_tenant=MAIN_TENANT)
    assert_that(
        response.items,
        all_of(has_item(main)),
        not_(has_item(sub)),
    )

    response = confd.funckeys.templates.get(wazo_tenant=SUB_TENANT)
    assert_that(
        response.items,
        all_of(has_item(sub), not_(has_item(main))),
    )

    response = confd.funckeys.templates.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(
        response.items,
        has_items(main, sub),
    )


@fixtures.funckey_template(name='template')
def test_get(funckey_template):
    response = confd.funckeys.templates(funckey_template['id']).get()
    assert_that(
        response.item,
        has_entries(
            id=not_(none()),
            tenant_uuid=MAIN_TENANT,
            name='template',
            keys=empty(),
        ),
    )


@fixtures.funckey_template(wazo_tenant=MAIN_TENANT)
@fixtures.funckey_template(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.funckeys.templates(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='FuncKeyTemplate'))

    response = confd.funckeys.templates(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


@fixtures.funckey_template(
    keys={'3': {'destination': {'type': 'custom', 'exten': '123'}}}
)
def test_get_position(funckey_template):
    response = confd.funckeys.templates(funckey_template['id'])(3).get()
    assert_that(response.item['destination'], has_entries(type='custom', exten='123'))


@fixtures.funckey_template(
    keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}},
    wazo_tenant=MAIN_TENANT,
)
@fixtures.funckey_template(
    keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}},
    wazo_tenant=SUB_TENANT,
)
def test_get_position_multi_tenant(main, sub):
    response = confd.funckeys.templates(main['id'])(1).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='FuncKeyTemplate'))

    response = confd.funckeys.templates(sub['id'])(1).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub['keys']['1']))


@fixtures.funckey_template(wazo_tenant=MAIN_TENANT)
@fixtures.funckey_template(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.funckeys.templates(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='FuncKeyTemplate'))

    response = confd.funckeys.templates(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.funckey_template(
    keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}},
    wazo_tenant=MAIN_TENANT,
)
@fixtures.funckey_template(
    keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}},
    wazo_tenant=SUB_TENANT,
)
def test_edit_position_multi_tenant(main, sub):
    response = confd.funckeys.templates(main['id'])(1).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='FuncKeyTemplate'))

    response = confd.funckeys.templates(sub['id'])(1).put(
        wazo_tenant=MAIN_TENANT,
        destination={'type': 'custom', 'exten': '456'},
    )
    response.assert_updated()


@fixtures.funckey_template()
def test_delete(funckey_template):
    response = confd.funckeys.templates(funckey_template['id']).delete()
    response.assert_deleted()
    url_get = confd.funckeys.templates(funckey_template['id']).get
    s.check_resource_not_found(url_get, 'FuncKeyTemplate')


@fixtures.funckey_template(wazo_tenant=MAIN_TENANT)
@fixtures.funckey_template(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.funckeys.templates(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='FuncKeyTemplate'))

    response = confd.funckeys.templates(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.funckey_template(
    keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}}
)
def test_delete_position(funckey_template):
    response = confd.funckeys.templates(funckey_template['id'])(1).delete()
    response.assert_deleted()
    url_get = confd.funckeys.templates(funckey_template['id'])(1).get
    s.check_resource_not_found(url_get, 'FuncKey')


@fixtures.funckey_template(
    keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}},
    wazo_tenant=MAIN_TENANT,
)
@fixtures.funckey_template(
    keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}},
    wazo_tenant=SUB_TENANT,
)
def test_delete_position_multi_tenant(main, sub):
    response = confd.funckeys.templates(main['id'])(1).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='FuncKeyTemplate'))

    response = confd.funckeys.templates(sub['id'])(1).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


def test_create_funckey_template_minimal_parameters():
    response = confd.funckeys.templates.post()
    response.assert_created('templates')

    assert_that(response.item, has_entries(keys={}, tenant_uuid=MAIN_TENANT, name=None))


def test_post_error_on_duplicate_destination():
    parameters = {
        'name': 'duplicate_dest',
        'keys': {
            '1': {'destination': {'type': 'custom', 'exten': '123'}},
            '2': {'destination': {'type': 'custom', 'exten': '123'}},
        },
    }

    response = confd.funckeys.templates.post(**parameters)
    response.assert_status(400)


@fixtures.funckey_template(
    keys={'1': {'destination': {'type': 'custom', 'exten': '123'}}}
)
def test_put_error_on_duplicate_destination(funckey_template):
    destination = {'destination': {'type': 'custom', 'exten': '123'}}

    response = confd.funckeys.templates(funckey_template['id'])(2).put(destination)
    response.assert_status(400)


def test_create_funckey_template_all_parameters():
    # Done in test_func_keys.py
    pass


def test_edit_funckey_template_position_all_parameters():
    # Done in test_func_keys.py
    pass
