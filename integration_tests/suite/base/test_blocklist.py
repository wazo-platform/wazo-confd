# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_exactly,
    empty,
    has_entries,
    has_item,
    has_items,
    is_not,
)

from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers import utils
from ..helpers.config import SUB_TENANT, SUB_TENANT2
from . import confd, create_confd

FAKE_UUID = '99999999-9999-4999-9999-999999999999'


def check_search_fuzzy(url, blocklist_number, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entries(field, blocklist_number[field])))
    assert_that(response.items, is_not(has_item(has_entries(field, hidden[field]))))


def check_search_exact(url, blocklist_number, hidden, field, term):
    response = url.get(**{field: blocklist_number[field]})
    assert_that(response.items, has_item(has_entries(uuid=blocklist_number['uuid'])))
    assert_that(response.items, is_not(has_item(has_entries(uuid=hidden['uuid']))))


def test_get_errors():
    fake_blocklist_number = confd.users.blocklist.numbers(FAKE_UUID).get
    s.check_resource_not_found(fake_blocklist_number, 'BlocklistNumber')


@fixtures.user()
@fixtures.user()
def test_search(user, other_user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    other_user_confd_client = create_confd(user_uuid=other_user['uuid'])
    numbers = [
        fixtures.users_blocklist_number(
            number='+18001235555', label='search', confd_client=user_confd_client
        ),
        fixtures.users_blocklist_number(
            number='+15551112222', label='hidden', confd_client=other_user_confd_client
        ),
    ]
    with utils.context_group(*numbers) as (blocklist_number, hidden):
        url = confd.users.blocklist.numbers
        fuzzy_searches = {
            'number': blocklist_number['number'],
            'label': blocklist_number['label'],
        }
        exact_searches = dict(
            **fuzzy_searches,
            user_uuid=user['uuid'],
        )

        for field, term in fuzzy_searches.items():
            response = url.get(search=term)
            assert_that(
                response.items, has_item(has_entries(field, blocklist_number[field]))
            )
            assert_that(
                response.items, is_not(has_item(has_entries(field, hidden[field])))
            )

        for field, term in exact_searches.items():
            response = url.get(**{field: term})
            assert_that(
                response.items, has_item(has_entries(uuid=blocklist_number['uuid']))
            )
            assert_that(
                response.items, is_not(has_item(has_entries(uuid=hidden['uuid'])))
            )


@fixtures.user()
@fixtures.user()
def test_list(user, other_user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    other_user_confd_client = create_confd(user_uuid=other_user['uuid'])
    numbers = [
        fixtures.users_blocklist_number(confd_client=user_confd_client),
        fixtures.users_blocklist_number(confd_client=user_confd_client),
        fixtures.users_blocklist_number(confd_client=other_user_confd_client),
        fixtures.users_blocklist_number(confd_client=other_user_confd_client),
    ]
    with utils.context_group(*numbers) as (first, second, third, fourth):
        response = confd.users.blocklist.numbers.get()
        assert_that(
            response.items,
            has_items(
                has_entries(
                    uuid=first['uuid'],
                    label=first['label'],
                    number=first['number'],
                    tenant_uuid=user['tenant_uuid'],
                    user_uuid=user['uuid'],
                    user_firstname=user['firstname'],
                    user_lastname=user['lastname'],
                ),
                has_entries(
                    uuid=second['uuid'],
                    label=second['label'],
                    number=second['number'],
                    tenant_uuid=user['tenant_uuid'],
                    user_uuid=user['uuid'],
                    user_firstname=user['firstname'],
                    user_lastname=user['lastname'],
                ),
                has_entries(
                    uuid=third['uuid'],
                    label=third['label'],
                    number=third['number'],
                    tenant_uuid=other_user['tenant_uuid'],
                    user_uuid=other_user['uuid'],
                    user_firstname=other_user['firstname'],
                    user_lastname=other_user['lastname'],
                ),
                has_entries(
                    uuid=fourth['uuid'],
                    label=fourth['label'],
                    number=fourth['number'],
                    tenant_uuid=other_user['tenant_uuid'],
                    user_uuid=other_user['uuid'],
                    user_firstname=other_user['firstname'],
                    user_lastname=other_user['lastname'],
                ),
            ),
        )


@fixtures.user(wazo_tenant=SUB_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT2)
def test_list_multitenant(user, other_user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    other_user_confd_client = create_confd(user_uuid=other_user['uuid'])
    numbers = [
        fixtures.users_blocklist_number(
            number='+18001235555', confd_client=user_confd_client
        ),
        fixtures.users_blocklist_number(
            number='+15551112222', confd_client=other_user_confd_client
        ),
    ]
    with utils.context_group(*numbers) as (blocklist_number1, blocklist_number2):
        # master tenant token
        url = confd.users.blocklist.numbers

        # recurse is false by default
        response = url.get()
        assert_that(response.items, empty())

        response = url.get(recurse=True)
        assert_that(
            response.items,
            has_items(
                has_entries(
                    uuid=blocklist_number1['uuid'],
                    label=blocklist_number1['label'],
                    number=blocklist_number1['number'],
                    tenant_uuid=user['tenant_uuid'],
                    user_uuid=user['uuid'],
                ),
                has_entries(
                    uuid=blocklist_number2['uuid'],
                    label=blocklist_number2['label'],
                    number=blocklist_number2['number'],
                    tenant_uuid=other_user['tenant_uuid'],
                    user_uuid=other_user['uuid'],
                ),
            ),
        )

        # sub tenant only
        response = url.get(wazo_tenant=user['tenant_uuid'])
        assert_that(
            response.items,
            contains_exactly(
                has_entries(
                    uuid=blocklist_number1['uuid'],
                    label=blocklist_number1['label'],
                    number=blocklist_number1['number'],
                    tenant_uuid=user['tenant_uuid'],
                    user_uuid=user['uuid'],
                ),
            ),
        )

        response = url.get(wazo_tenant=other_user['tenant_uuid'])
        assert_that(
            response.items,
            contains_exactly(
                has_entries(
                    uuid=blocklist_number2['uuid'],
                    label=blocklist_number2['label'],
                    number=blocklist_number2['number'],
                    tenant_uuid=other_user['tenant_uuid'],
                    user_uuid=other_user['uuid'],
                ),
            ),
        )


@fixtures.user()
def test_sorting_offset_limit(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    numbers = [
        fixtures.users_blocklist_number(
            number='+11111111111', label='sort1', confd_client=user_confd_client
        ),
        fixtures.users_blocklist_number(
            number='+11111111112', label='sort2', confd_client=user_confd_client
        ),
    ]
    with utils.context_group(*numbers) as (blocklist_number1, blocklist_number2):
        url = confd.users.blocklist.numbers.get
        list_args = (url, blocklist_number1, blocklist_number2, 'label', 'sort')
        list_kwargs = {'id_field': 'uuid'}

        s.check_sorting(*list_args, **list_kwargs)
        s.check_offset(*list_args, **list_kwargs)
        s.check_limit(*list_args, **list_kwargs)

        list_args = (url, blocklist_number1, blocklist_number2, 'number', '+111111111')
        s.check_sorting(*list_args, **list_kwargs)
        s.check_offset(*list_args, **list_kwargs)
        s.check_limit(*list_args, **list_kwargs)


@fixtures.user()
def test_get(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    with fixtures.users_blocklist_number(
        confd_client=user_confd_client
    ) as blocklist_number:
        response = confd.users.blocklist.numbers(blocklist_number['uuid']).get()
        assert_that(
            response.item,
            has_entries(
                uuid=blocklist_number['uuid'],
                label=blocklist_number['label'],
                number=blocklist_number['number'],
                tenant_uuid=user['tenant_uuid'],
                user_uuid=user['uuid'],
                user_firstname=user['firstname'],
                user_lastname=user['lastname'],
            ),
        )


@fixtures.user()
def test_head_lookup(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    with fixtures.users_blocklist_number(
        confd_client=user_confd_client
    ) as blocklist_number:
        response = confd.users(user['uuid']).blocklist.numbers.head(
            number_exact=blocklist_number['number']
        )
        response.assert_status(204)
        response.assert_location(
            'blocklist_numbers',
            url_segment=f'blocklist/numbers/{blocklist_number["uuid"]}',
        )
        response.assert_headers(
            ('Wazo-Blocklist-Number-UUID', blocklist_number['uuid']),
            ('Wazo-Blocklist-Number-Label', ''),
        )


@fixtures.user()
def test_user_list(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    numbers = [
        fixtures.users_blocklist_number(confd_client=user_confd_client),
        fixtures.users_blocklist_number(confd_client=user_confd_client),
    ]
    with utils.context_group(*numbers) as (first, second):
        response = confd.users(user['uuid']).blocklist.numbers.get()
        assert_that(
            response.items,
            has_items(
                has_entries(
                    uuid=first['uuid'],
                    label=first['label'],
                    number=first['number'],
                    tenant_uuid=user['tenant_uuid'],
                    user_uuid=user['uuid'],
                    user_firstname=user['firstname'],
                    user_lastname=user['lastname'],
                ),
                has_entries(
                    uuid=second['uuid'],
                    label=second['label'],
                    number=second['number'],
                    tenant_uuid=user['tenant_uuid'],
                    user_uuid=user['uuid'],
                    user_firstname=user['firstname'],
                    user_lastname=user['lastname'],
                ),
            ),
        )
