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
    not_,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from . import create_confd

FAKE_UUID = '99999999-9999-4999-9999-999999999999'


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'number', 123)
    s.check_bogus_field_returns_error(url, 'number', [])
    s.check_bogus_field_returns_error(url, 'number', None)
    s.check_bogus_field_returns_error(url, 'number', True)
    s.check_bogus_field_returns_error(url, 'number', {})
    s.check_bogus_field_returns_error(url, 'number', 'a' * 1024)
    s.check_bogus_field_returns_error(
        url, 'number', '123', message=r'Invalid E.164 phone number'
    )
    s.check_bogus_field_returns_error(
        url, 'label', 123, required_field={'number': '+123'}
    )
    s.check_bogus_field_returns_error(
        url, 'label', [], required_field={'number': '+123'}
    )
    s.check_bogus_field_returns_error(
        url, 'label', True, required_field={'number': '+123'}
    )
    s.check_bogus_field_returns_error(
        url, 'label', {}, required_field={'number': '+123'}
    )
    s.check_bogus_field_returns_error(url, 'label', 'a' * 1025, {'number': '+123'})


def check_search_fuzzy(url, blocklist_number, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entries(field, blocklist_number[field])))
    assert_that(response.items, is_not(has_item(has_entries(field, hidden[field]))))


def check_search_exact(url, blocklist_number, hidden, field, term):
    response = url.get(**{field: blocklist_number[field]})
    assert_that(response.items, has_item(has_entries(uuid=blocklist_number['uuid'])))
    assert_that(response.items, is_not(has_item(has_entries(uuid=hidden['uuid']))))


@fixtures.user()
def test_get_errors(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    fake_blocklist_number = user_confd_client.users.me.blocklist.numbers(FAKE_UUID).get
    s.check_resource_not_found(fake_blocklist_number, 'BlocklistNumber')


@fixtures.user()
def test_delete_errors(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    fake_blocklist_number = user_confd_client.users.me.blocklist.numbers(
        FAKE_UUID
    ).delete
    s.check_resource_not_found(fake_blocklist_number, 'BlocklistNumber')


@fixtures.user()
def test_put_not_found(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    fake_blocklist_number = user_confd_client.users.me.blocklist.numbers(FAKE_UUID).put
    s.check_resource_not_found(fake_blocklist_number, 'BlocklistNumber')


@fixtures.user()
def test_put_bogus_fields(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    with fixtures.users_blocklist_number(
        confd_client=user_confd_client
    ) as blocklist_number:
        url = user_confd_client.users.me.blocklist.numbers(blocklist_number['uuid']).put
        error_checks(url)


@fixtures.user()
def test_put_conflict(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    with fixtures.users_blocklist_number(
        confd_client=user_confd_client
    ) as blocklist_number1:
        with fixtures.users_blocklist_number(
            number='+18005551234', confd_client=user_confd_client
        ) as blocklist_number2:
            blocklist_number1['number'] = blocklist_number2['number']
            response = user_confd_client.users.me.blocklist.numbers(
                blocklist_number1['uuid']
            ).put(**blocklist_number1)
            response.assert_match(400, e.resource_exists(resource='BlocklistNumber'))


@fixtures.user()
def test_post_bogus_fields(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    url = user_confd_client.users.me.blocklist.numbers.post
    error_checks(url)


@fixtures.user()
def test_post_conflict(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    with fixtures.users_blocklist_number(
        number='+18005551234', confd_client=user_confd_client
    ) as blocklist_number:
        url = user_confd_client.users.me.blocklist.numbers.post

        response = url(number=blocklist_number['number'])
        response.assert_match(400, e.resource_exists(resource='BlocklistNumber'))


@fixtures.user()
def test_search(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    number1 = fixtures.users_blocklist_number(
        number='+18001235555', label='search', confd_client=user_confd_client
    )
    number2 = fixtures.users_blocklist_number(
        number='+15551112222', label='hidden', confd_client=user_confd_client
    )
    with number1 as blocklist_number, number2 as hidden:
        url = user_confd_client.users.me.blocklist.numbers
        fuzzy_searches = {
            'number': blocklist_number['number'],
            'label': blocklist_number['label'],
        }
        exact_searches = dict(
            **fuzzy_searches,
        )

        for field, term in fuzzy_searches.items():
            check_search_fuzzy(url, blocklist_number, hidden, field, term)

        for field, term in exact_searches.items():
            check_search_exact(url, blocklist_number, hidden, field, term)


@fixtures.user()
@fixtures.user()
def test_search_users_isolated(user1, user2):
    user1_confd_client = create_confd(user_uuid=user1['uuid'])
    user2_confd_client = create_confd(user_uuid=user2['uuid'])

    number1 = fixtures.users_blocklist_number(
        number='+18001235555', confd_client=user1_confd_client
    )
    number2 = fixtures.users_blocklist_number(
        number='+15551112222', confd_client=user2_confd_client
    )
    with number1 as blocklist_number1, number2 as blocklist_number2:
        response1 = user1_confd_client.users.me.blocklist.numbers.get()

        assert_that(response1.items, contains_exactly(blocklist_number1))

        response2 = user2_confd_client.users.me.blocklist.numbers.get()

        assert_that(response2.items, contains_exactly(blocklist_number2))


@fixtures.user()
def test_list(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    number1 = fixtures.users_blocklist_number(confd_client=user_confd_client)
    number2 = fixtures.users_blocklist_number(confd_client=user_confd_client)
    with number1 as first, number2 as second:
        response = user_confd_client.users.me.blocklist.numbers.get()
        assert_that(response.items, has_items(first, second))


@fixtures.user()
def test_sorting_offset_limit(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    number1 = fixtures.users_blocklist_number(
        number='+11111111111', label='sort1', confd_client=user_confd_client
    )
    number2 = fixtures.users_blocklist_number(
        number='+11111111112', label='sort2', confd_client=user_confd_client
    )
    with number1 as blocklist_number1, number2 as blocklist_number2:
        url = user_confd_client.users.me.blocklist.numbers.get
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
        response = user_confd_client.users.me.blocklist.numbers(
            blocklist_number['uuid']
        ).get()
        assert_that(
            response.item,
            has_entries(
                uuid=blocklist_number['uuid'],
                label=blocklist_number['label'],
                number=blocklist_number['number'],
            ),
        )


@fixtures.user()
def test_create_minimal_parameters(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    response = user_confd_client.users.me.blocklist.numbers.post({'number': '+112'})
    response.assert_created(
        'user_me_blocklist_numbers', url_segment='blocklist/numbers'
    )

    assert_that(
        response.item,
        has_entries(
            uuid=not_(empty()),
            number='+112',
            label=None,
        ),
    )

    user_confd_client.users.me.blocklist.numbers(
        response.item['uuid']
    ).delete().assert_deleted()


@fixtures.user()
def test_create_all_parameters(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    parameters = {
        'number': '+18001235567',
        'label': 'Here',
    }

    response = user_confd_client.users.me.blocklist.numbers.post(parameters)
    response.assert_created(
        'user_me_blocklist_numbers', url_segment='blocklist/numbers'
    )

    assert_that(response.item, has_entries(uuid=not_(empty()), **parameters))

    user_confd_client.users.me.blocklist.numbers(
        response.item['uuid']
    ).delete().assert_deleted()


@fixtures.user()
def test_edit_minimal_parameters(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    with fixtures.users_blocklist_number(
        confd_client=user_confd_client
    ) as blocklist_number:
        response = user_confd_client.users.me.blocklist.numbers(
            blocklist_number['uuid']
        ).put()
        response.assert_updated()


@fixtures.user()
def test_edit_all_parameters(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    with fixtures.users_blocklist_number(
        confd_client=user_confd_client
    ) as blocklist_number:
        parameters = {
            'number': '+18001235567',
            'label': 'Here',
        }

        response = user_confd_client.users.me.blocklist.numbers(
            blocklist_number['uuid']
        ).put(**parameters)
        response.assert_updated()

        response = user_confd_client.users.me.blocklist.numbers(
            blocklist_number['uuid']
        ).get()
        assert_that(response.item, has_entries(parameters))


@fixtures.user()
def test_bus_events(user):
    user_confd_client = create_confd(user_uuid=user['uuid'])
    url = user_confd_client.users.me.blocklist.numbers
    headers = {}

    blocklist_number = s.check_event(
        'user_blocklist_number_created', headers, url.post, {'number': '+111'}
    )
    s.check_event(
        'user_blocklist_number_edited',
        headers,
        url(blocklist_number.item['uuid']).put,
        {'number': '+112'},
    )
    s.check_event(
        'user_blocklist_number_deleted',
        headers,
        url(blocklist_number.item['uuid']).delete,
    )
