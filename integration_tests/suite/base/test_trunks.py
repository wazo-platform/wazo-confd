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
    fake_trunk = confd.trunks(999999).get
    s.check_resource_not_found(fake_trunk, 'Trunk')


def test_delete_errors():
    fake_trunk = confd.trunks(999999).delete
    s.check_resource_not_found(fake_trunk, 'Trunk')


def test_post_errors():
    url = confd.trunks.post
    error_checks(url)


def test_put_errors():
    with fixtures.trunk() as trunk:
        url = confd.trunks(trunk['id']).put
        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'context', 123)
    s.check_bogus_field_returns_error(url, 'context', [])
    s.check_bogus_field_returns_error(url, 'context', {})
    s.check_bogus_field_returns_error(url, 'context', 'invalid')
    s.check_bogus_field_returns_error(url, 'twilio_incoming', 123)
    s.check_bogus_field_returns_error(url, 'twilio_incoming', [])
    s.check_bogus_field_returns_error(url, 'twilio_incoming', {})


def test_search():
    with fixtures.context(name='search') as _, fixtures.context(name='hidden') as __, fixtures.trunk(context='search') as trunk, fixtures.trunk(context='hidden') as hidden:
        url = confd.trunks
        searches = {'context': 'search'}

        for field, term in searches.items():
            check_search(url, trunk, hidden, field, term)



def check_search(url, trunk, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, trunk[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: trunk[field]})
    assert_that(response.items, has_item(has_entry('id', trunk['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def test_sorting_offset_limit():
    with fixtures.context(name='sort1') as _, fixtures.context(name='sort2') as __, fixtures.trunk(context='sort1') as trunk1, fixtures.trunk(context='sort2') as trunk2:
        url = confd.trunks.get
        s.check_sorting(url, trunk1, trunk2, 'context', 'sort')

        s.check_offset(url, trunk1, trunk2, 'context', 'sort')
        s.check_offset_legacy(url, trunk1, trunk2, 'context', 'sort')

        s.check_limit(url, trunk1, trunk2, 'context', 'sort')



def test_list_multi_tenant():
    with fixtures.trunk(wazo_tenant=MAIN_TENANT) as main, fixtures.trunk(wazo_tenant=SUB_TENANT) as sub:
        response = confd.trunks.get(wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            all_of(has_item(main)), not_(has_item(sub)),
        )

        response = confd.trunks.get(wazo_tenant=SUB_TENANT)
        assert_that(
            response.items,
            all_of(has_item(sub), not_(has_item(main))),
        )

        response = confd.trunks.get(wazo_tenant=MAIN_TENANT, recurse=True)
        assert_that(
            response.items,
            has_items(main, sub),
        )



def test_get():
    with fixtures.trunk() as trunk:
        response = confd.trunks(trunk['id']).get()
        assert_that(response.item, has_entries(
            id=trunk['id'],
            context=trunk['context'],
            twilio_incoming=trunk['twilio_incoming'],
            endpoint_sip=none(),
            endpoint_custom=none(),
            endpoint_iax=none(),
            outcalls=empty(),
            register_iax=none(),
            register_sip=none(),
        ))



def test_get_multi_tenant():
    with fixtures.trunk(wazo_tenant=MAIN_TENANT) as main, fixtures.trunk(wazo_tenant=SUB_TENANT) as sub:
        response = confd.trunks(main['id']).get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Trunk'))

        response = confd.trunks(sub['id']).get(wazo_tenant=MAIN_TENANT)
        assert_that(response.item, has_entries(**sub))



def test_create_minimal_parameters():
    response = confd.trunks.post()
    response.assert_created('trunks')

    assert_that(response.item, has_entries(id=not_(empty()), tenant_uuid=MAIN_TENANT))


def test_create_all_parameters():
    with fixtures.context() as context:
        parameters = {
            'context': context['name'],
            'twilio_incoming': True,
        }
        response = confd.trunks.post(**parameters)
        response.assert_created('trunks')

        assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))



def test_create_multi_tenant():
    with fixtures.context(wazo_tenant=MAIN_TENANT) as context:
        response = confd.trunks.post(context=context['name'], wazo_tenant=SUB_TENANT)
        response.assert_match(400, e.different_tenant())



def test_edit_minimal_parameters():
    with fixtures.trunk() as trunk:
        parameters = {}

        response = confd.trunks(trunk['id']).put(**parameters)
        response.assert_updated()



def test_edit_all_parameters():
    with fixtures.context(name='not_default') as context, fixtures.trunk() as trunk:
        parameters = {
            'context': context['name'],
            'twilio_incoming': True,
        }

        response = confd.trunks(trunk['id']).put(**parameters)
        response.assert_updated()

        response = confd.trunks(trunk['id']).get()
        assert_that(response.item, has_entries(parameters))



def test_edit_multi_tenant():
    with fixtures.context() as context, fixtures.trunk(wazo_tenant=MAIN_TENANT) as main, fixtures.trunk(wazo_tenant=SUB_TENANT) as sub:
        response = confd.trunks(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Trunk'))

        response = confd.trunks(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()

        response = confd.trunks(sub['id']).put(context=context['name'], wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_delete():
    with fixtures.trunk() as trunk:
        response = confd.trunks(trunk['id']).delete()
        response.assert_deleted()



def test_delete_multi_tenant():
    with fixtures.trunk(wazo_tenant=MAIN_TENANT) as main, fixtures.trunk(wazo_tenant=SUB_TENANT) as sub:
        response = confd.trunks(main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Trunk'))

        response = confd.trunks(sub['id']).delete(wazo_tenant=MAIN_TENANT)
        response.assert_deleted()

