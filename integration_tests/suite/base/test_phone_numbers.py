# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains_string,
    empty,
    has_item,
    has_items,
    has_entries,
    is_not,
    matches_regexp,
    none,
    not_,
    has_length,
    starts_with,
)
import pytest
from . import confd
from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from ..helpers.fixtures import phone_number_range  # noqa: F401

FAKE_UUID = '99999999-9999-4999-9999-999999999999'


def test_get_errors():
    fake_phone_number = confd.phone_numbers(FAKE_UUID).get
    s.check_resource_not_found(fake_phone_number, 'PhoneNumber')


def test_delete_errors():
    fake_phone_number = confd.phone_numbers(FAKE_UUID).delete
    s.check_resource_not_found(fake_phone_number, 'PhoneNumber')


@fixtures.phone_number()
def test_put_errors(phone_number):
    fake_phone_number = confd.phone_numbers(FAKE_UUID).put
    s.check_resource_not_found(fake_phone_number, 'PhoneNumber')

    url = confd.phone_numbers(phone_number['uuid']).put
    error_checks(url)
    unique_error_checks_put(phone_number)


def test_post_errors():
    url = confd.phone_numbers.post
    error_checks(url)
    unique_error_checks_post(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'number', 123)
    s.check_bogus_field_returns_error(url, 'number', [])
    s.check_bogus_field_returns_error(url, 'number', None)
    s.check_bogus_field_returns_error(url, 'number', True)
    s.check_bogus_field_returns_error(url, 'number', {})
    s.check_bogus_field_returns_error(url, 'number', 'a' * 1024)
    s.check_bogus_field_returns_error(url, 'caller_id_name', 123)
    s.check_bogus_field_returns_error(url, 'caller_id_name', [])
    s.check_bogus_field_returns_error(url, 'caller_id_name', True)
    s.check_bogus_field_returns_error(url, 'caller_id_name', {})
    s.check_bogus_field_returns_error(url, 'caller_id_name', 'a' * 1024)
    s.check_bogus_field_returns_error(url, 'main', 123)
    s.check_bogus_field_returns_error(url, 'main', '42')
    s.check_bogus_field_returns_error(url, 'main', None)
    s.check_bogus_field_returns_error(url, 'main', [])
    s.check_bogus_field_returns_error(url, 'main', {})
    s.check_bogus_field_returns_error(url, 'shared', 123)
    s.check_bogus_field_returns_error(url, 'shared', '42')
    s.check_bogus_field_returns_error(url, 'shared', None)
    s.check_bogus_field_returns_error(url, 'shared', [])
    s.check_bogus_field_returns_error(url, 'shared', {})


@fixtures.phone_number(number='+18005551234', main=True)
def unique_error_checks_put(first, second):
    first['main'] = True
    response = confd.phone_numbers(first['uuid']).put(**first)
    response.assert_match(400, e.resource_exists(resource='PhoneNumber'))

    first['main'] = False
    first['number'] = second['number']
    response = confd.phone_numbers(first['uuid']).put(**first)
    response.assert_match(400, e.resource_exists(resource='PhoneNumber'))


@fixtures.phone_number(number='+18005551234', main=True)
def unique_error_checks_post(url, existing):
    response = url(number='+15551234567', main=True)
    response.assert_match(400, e.resource_exists(resource='PhoneNumber'))

    response = url(number=existing['number'])
    response.assert_match(400, e.resource_exists(resource='PhoneNumber'))


@fixtures.phone_number(
    number='+18001235555', main=True, shared=True, caller_id_name='search'
)
@fixtures.phone_number(
    number='+15551112222', main=False, shared=False, caller_id_name='hidden'
)
def test_search(phone_number, hidden):
    url = confd.phone_numbers
    fuzzy_searches = {
        'number': phone_number['number'],
        'caller_id_name': phone_number['caller_id_name'],
    }
    exact_searches = dict(
        main=True,
        shared=True,
        **fuzzy_searches,
    )

    for field, term in fuzzy_searches.items():
        check_search_fuzzy(url, phone_number, hidden, field, term)

    for field, term in exact_searches.items():
        check_search_exact(url, phone_number, hidden, field, term)


def check_search_fuzzy(url, phone_number, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entries(field, phone_number[field])))
    assert_that(response.items, is_not(has_item(has_entries(field, hidden[field]))))


def check_search_exact(url, phone_number, hidden, field, term):
    response = url.get(**{field: phone_number[field]})
    assert_that(response.items, has_item(has_entries(uuid=phone_number['uuid'])))
    assert_that(response.items, is_not(has_item(has_entries(uuid=hidden['uuid']))))


@fixtures.phone_number(wazo_tenant=MAIN_TENANT)
@fixtures.phone_number(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.phone_numbers.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.phone_numbers.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.phone_numbers.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.phone_number(number='+11111111111', caller_id_name='sort1')
@fixtures.phone_number(number='+11111111112', caller_id_name='sort2')
def test_sorting_offset_limit(phone_number1, phone_number2):
    url = confd.phone_numbers.get
    list_args = (url, phone_number1, phone_number2, 'caller_id_name', 'sort')
    list_kwargs = {'id_field': 'uuid'}

    s.check_sorting(*list_args, **list_kwargs)
    s.check_offset(*list_args, **list_kwargs)
    s.check_limit(*list_args, **list_kwargs)

    list_args = (url, phone_number1, phone_number2, 'number', '+111111111')
    s.check_sorting(*list_args, **list_kwargs)
    s.check_offset(*list_args, **list_kwargs)
    s.check_limit(*list_args, **list_kwargs)


@fixtures.phone_number()
def test_get(phone_number):
    response = confd.phone_numbers(phone_number['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            uuid=phone_number['uuid'],
            tenant_uuid=MAIN_TENANT,
            caller_id_name=phone_number['caller_id_name'],
            main=phone_number['main'],
            shared=phone_number['shared'],
        ),
    )


@fixtures.phone_number(wazo_tenant=MAIN_TENANT)
@fixtures.phone_number(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.phone_numbers(main['uuid']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='PhoneNumber'))

    response = confd.phone_numbers(sub['uuid']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.phone_numbers.post({'number': '112'})
    response.assert_created('phone_numbers', url_segment='phone-numbers')

    assert_that(response.item, has_entries(uuid=not_(empty()), tenant_uuid=MAIN_TENANT))

    confd.phone_numbers(response.item['uuid']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'number': '+18001235567',
        'caller_id_name': 'Here',
        'main': True,
        'shared': True,
    }

    response = confd.phone_numbers.post(parameters)
    response.assert_created('phone_numbers', url_segment='phone-numbers')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.phone_numbers(response.item['uuid']).delete().assert_deleted()


def test_create_range():
    parameters = {'start_number': '+18001235560', 'end_number': '+18001235569'}

    response = confd.phone_numbers.ranges.post(parameters)
    response.assert_status(201)

    assert_that(
        response.item,
        has_entries(
            created=has_items(has_entries(uuid=not_(none()))),
            links=has_items(
                has_entries(
                    rel=contains_string('phone_numbers'),
                    href=contains_string('phone-numbers'),
                )
            ),
            total=10,
        ),
        str(response.item),
    )

    for phone_number in response.item['created']:
        phone_number_resource = confd.phone_numbers(phone_number['uuid']).get()
        assert_that(
            phone_number_resource.item,
            has_entries(
                number=all_of(
                    starts_with('+1800123556'),
                ),
            ),
            str(phone_number_resource),
        )
        confd.phone_numbers(phone_number['uuid']).delete().assert_deleted()


def test_create_range_singleton():
    parameters = {'start_number': '+18001235560', 'end_number': '+18001235560'}

    response = confd.phone_numbers.ranges.post(parameters, wazo_tenant=MAIN_TENANT)
    response.assert_status(201)

    assert_that(
        response.item,
        has_entries(
            created=all_of(has_items(has_entries(uuid=not_(none()))), has_length(1)),
            links=all_of(
                has_items(
                    has_entries(
                        rel=contains_string('phone_numbers'),
                        href=contains_string('phone-numbers'),
                    )
                ),
                has_length(1),
            ),
            total=1,
        ),
        str(response.item),
    )

    for phone_number in response.item['created']:
        phone_number_resource = confd.phone_numbers(phone_number['uuid']).get()
        assert_that(
            phone_number_resource.item,
            has_entries(
                number='+18001235560',
            ),
            str(phone_number_resource),
        )
        confd.phone_numbers(phone_number['uuid']).delete().assert_deleted()


def test_create_range_too_large():
    parameters = {'start_number': '+18001230000', 'end_number': '+18001249999'}

    response = confd.phone_numbers.ranges.post(parameters)
    response.assert_status(400)

    assert_that(response.json, has_item(contains_string('range size')))


def test_create_range_bad_order():
    parameters = {'start_number': '+18001230000', 'end_number': '+18001225000'}

    response = confd.phone_numbers.ranges.post(parameters)
    response.assert_status(400)

    assert_that(
        response.json,
        has_item(contains_string('start phone number must precede end phone number')),
    )


@pytest.mark.parametrize(
    'phone_number_range',
    [
        dict(
            start_number='+18001230000',
            end_number='+18001230999',
            wazo_tenant=SUB_TENANT,
        )
    ],
    indirect=True,
)
def test_create_range_multi_tenant(phone_number_range):  # noqa: F811
    parameters = {'start_number': '+18001230500', 'end_number': '+18001231499'}

    response = confd.phone_numbers.ranges.post(parameters, wazo_tenant=MAIN_TENANT)
    response.assert_status(201)

    assert_that(
        response.item,
        has_entries(
            created=all_of(has_items(has_entries(uuid=not_(none()))), has_length(1000)),
            links=all_of(
                has_items(
                    has_entries(
                        rel=contains_string('phone_numbers'),
                        href=contains_string('phone-numbers'),
                    )
                ),
                has_length(1000),
            ),
            total=1000,
        ),
        str(response.item),
    )

    for phone_number in response.item['created']:
        phone_number_resource = confd.phone_numbers(phone_number['uuid']).get()
        assert_that(
            phone_number_resource.item,
            has_entries(
                number=starts_with('+1800123'),
                tenant_uuid=MAIN_TENANT,
            ),
            str(phone_number_resource),
        )
        confd.phone_numbers(phone_number['uuid']).delete().assert_deleted()

    for number in phone_number_range:
        phone_number_resource = confd.phone_numbers(number['uuid']).get()
        assert_that(
            phone_number_resource.item,
            has_entries(
                number=starts_with('+1800123'),
                tenant_uuid=SUB_TENANT,
            ),
            str(phone_number_resource),
        )


@pytest.mark.parametrize(
    'phone_number_range',
    [
        dict(
            start_number='+18001230000',
            end_number='+18001230999',
            wazo_tenant=MAIN_TENANT,
        )
    ],
    indirect=True,
)
def test_create_range_idempotence(phone_number_range):  # noqa: F811
    parameters = {'start_number': '+18001230500', 'end_number': '+18001231499'}

    response = confd.phone_numbers.ranges.post(parameters, wazo_tenant=MAIN_TENANT)
    response.assert_status(201)

    assert_that(
        response.item,
        has_entries(
            created=all_of(has_items(has_entries(uuid=not_(none()))), has_length(500)),
            links=all_of(
                has_items(
                    has_entries(
                        rel=contains_string('phone_numbers'),
                        href=contains_string('phone-numbers'),
                    )
                ),
                has_length(1000),
            ),
            total=1000,
        ),
        str(response.item),
    )

    for phone_number in response.item['created']:
        phone_number_resource = confd.phone_numbers(phone_number['uuid']).get()
        assert_that(
            phone_number_resource.item,
            has_entries(
                number=matches_regexp(r'^\+1800123[01][0-9]{3}$'),
            ),
            str(phone_number_resource),
        )
        confd.phone_numbers(phone_number['uuid']).delete().assert_deleted()

    for phone_number in phone_number_range:
        phone_number_resource = confd.phone_numbers(phone_number['uuid']).get()
        assert_that(
            phone_number_resource.item,
            has_entries(
                number=matches_regexp(r'^\+18001230[0-9]{3}$'),
            ),
            str(phone_number_resource),
        )


@fixtures.phone_number()
def test_edit_minimal_parameters(phone_number):
    response = confd.phone_numbers(phone_number['uuid']).put()
    response.assert_updated()


@fixtures.phone_number()
def test_edit_all_parameters(phone_number):
    parameters = {
        'number': '+18001235567',
        'caller_id_name': 'Here',
        'main': True,
        'shared': True,
    }

    response = confd.phone_numbers(phone_number['uuid']).put(**parameters)
    response.assert_updated()

    response = confd.phone_numbers(phone_number['uuid']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.phone_number(wazo_tenant=MAIN_TENANT)
@fixtures.phone_number(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.phone_numbers(main['uuid']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='PhoneNumber'))

    response = confd.phone_numbers(sub['uuid']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.phone_number(wazo_tenant=MAIN_TENANT)
@fixtures.phone_number(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.phone_numbers(main['uuid']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='PhoneNumber'))

    response = confd.phone_numbers(sub['uuid']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.phone_number()
def test_bus_events(phone_number):
    url = confd.phone_numbers(phone_number['uuid'])
    headers = {'tenant_uuid': phone_number['tenant_uuid']}

    s.check_event(
        'phone_number_created', headers, confd.phone_numbers.post, {'number': '111'}
    )
    s.check_event('phone_number_edited', headers, url.put)
    s.check_event('phone_number_deleted', headers, url.delete)
