# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_entries,
    contains_exactly,
    contains_inanyorder,
    empty,
)

from . import confd
from ..helpers import associations as a, fixtures, scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT


@fixtures.context(
    user_ranges=[
        {'start': '1000', 'end': '1099'},
        {'start': '1200', 'end': '1499'},
        {'start': '1800', 'end': '1899'},
    ],
    group_ranges=[
        {'start': '2000', 'end': '2999'},
    ],
    queue_ranges=[
        {'start': '3000', 'end': '3999'},
    ],
    conference_room_ranges=[
        {'start': '4000', 'end': '4999'},
    ],
)
@fixtures.context(
    type='incall',
    incall_ranges=[
        {'start': '8005551000', 'end': '8005551009'},
    ],
)
def test_search_all_types(internal_context, incoming_context):
    response = confd.contexts(internal_context['id']).ranges('user').get()
    assert_that(
        response.json,
        has_entries(
            total=3,
            items=contains_inanyorder(
                {'start': '1000', 'end': '1099'},
                {'start': '1200', 'end': '1499'},
                {'start': '1800', 'end': '1899'},
            ),
        ),
    )

    response = confd.contexts(internal_context['id']).ranges('group').get()
    assert_that(
        response.json,
        has_entries(
            total=1,
            items=contains_inanyorder(
                {'start': '2000', 'end': '2999'},
            ),
        ),
    )

    response = confd.contexts(internal_context['id']).ranges('queue').get()
    assert_that(
        response.json,
        has_entries(
            total=1,
            items=contains_inanyorder(
                {'start': '3000', 'end': '3999'},
            ),
        ),
    )

    response = confd.contexts(internal_context['id']).ranges('conference').get()
    assert_that(
        response.json,
        has_entries(
            total=1,
            items=contains_inanyorder(
                {'start': '4000', 'end': '4999'},
            ),
        ),
    )

    response = confd.contexts(incoming_context['id']).ranges('incall').get()
    assert_that(
        response.json,
        has_entries(
            total=1,
            items=contains_inanyorder(
                {'start': '8005551000', 'end': '8005551009'},
            ),
        ),
    )


@fixtures.context(
    user_ranges=[
        {'start': '1000', 'end': '1999'},
    ],
)
@fixtures.user()
@fixtures.line_sip()
def test_search_availability(context, user, line):
    @fixtures.extension(context=context['name'], exten='1005')
    def aux(extension):
        with a.user_line(user, line), a.line_extension(line, extension):
            response = (
                confd.contexts(context['id'])
                .ranges('user')
                .get(availability='available')
            )
            assert_that(
                response.json,
                has_entries(
                    total=2,
                    items=contains_inanyorder(
                        {'start': '1000', 'end': '1004'},
                        {'start': '1006', 'end': '1999'},
                    ),
                ),
            )

            response = (
                confd.contexts(context['id']).ranges('user').get(availability='all')
            )
            assert_that(
                response.json,
                has_entries(
                    total=1,
                    items=contains_inanyorder(
                        {'start': '1000', 'end': '1999'},
                    ),
                ),
            )

            response = (
                confd.contexts(context['id']).ranges('user').get(availability='unknown')
            )
            response.assert_status(400)

    aux()


@fixtures.context(
    user_ranges=[
        {'start': '00', 'end': '99'},
        {'start': '0001', 'end': '0499'},
    ],
)
def test_search_partial_exten(context):
    response = confd.contexts(context['id']).ranges('user').get(search='11')
    assert_that(
        response.json,
        has_entries(
            total=6,
            items=contains_inanyorder(
                {'start': '11', 'end': '11'},
                {'start': '0011', 'end': '0011'},
                {'start': '0110', 'end': '0119'},
                {'start': '0211', 'end': '0211'},
                {'start': '0311', 'end': '0311'},
                {'start': '0411', 'end': '0411'},
            ),
        ),
    )

    response = confd.contexts(context['id']).ranges('user').get(search='0011')
    assert_that(
        response.json,
        has_entries(
            total=1,
            items=contains_inanyorder(
                {'start': '0011', 'end': '0011'},
            ),
        ),
    )

    response = confd.contexts(context['id']).ranges('user').get(search='10000')
    assert_that(
        response.json,
        has_entries(
            total=0,
            items=empty(),
        ),
    )


@fixtures.context(
    user_ranges=[
        {'start': '100', 'end': '119'},
        {'start': '000', 'end': '099'},
        {'start': '070', 'end': '199'},
    ],
)
def test_search_overlapping_ranges(context):
    response = confd.contexts(context['id']).ranges('user').get()
    print(response)
    assert_that(
        response.json,
        has_entries(
            total=1,
            items=contains_inanyorder(
                {'start': '000', 'end': '199'},
            ),
        ),
    )


@fixtures.context(
    user_ranges=[
        {'start': '00', 'end': '99'},
        {'start': '0001', 'end': '0499'},
    ],
)
def test_search_pagination(context):
    response = confd.contexts(context['id']).ranges('user').get(search='11', limit=2)
    assert_that(
        response.json,
        has_entries(
            total=6,
            items=contains_inanyorder(
                {'start': '11', 'end': '11'},
                {'start': '0011', 'end': '0011'},
                # {'start': '0110', 'end': '0119'},
                # {'start': '0211', 'end': '0211'},
                # {'start': '0311', 'end': '0311'},
                # {'start': '0411', 'end': '0411'},
            ),
        ),
    )

    response = (
        confd.contexts(context['id']).ranges('user').get(search='11', offset=4, limit=3)
    )
    assert_that(
        response.json,
        has_entries(
            total=6,
            items=contains_inanyorder(
                # {'start': '11', 'end': '11'},
                # {'start': '0011', 'end': '0011'},
                # {'start': '0110', 'end': '0119'},
                # {'start': '0211', 'end': '0211'},
                {'start': '0311', 'end': '0311'},
                {'start': '0411', 'end': '0411'},
            ),
        ),
    )

    response = confd.contexts(context['id']).ranges('user').get(search='11', offset=2)
    assert_that(
        response.json,
        has_entries(
            total=6,
            items=contains_inanyorder(
                # {'start': '11', 'end': '11'},
                # {'start': '0011', 'end': '0011'},
                {'start': '0110', 'end': '0119'},
                {'start': '0211', 'end': '0211'},
                {'start': '0311', 'end': '0311'},
                {'start': '0411', 'end': '0411'},
            ),
        ),
    )


@fixtures.context(
    user_ranges=[
        {'start': '100', 'end': '999'},
        {'start': '5999', 'end': '6000'},
    ],
)
def test_search_order(context):
    response = (
        confd.contexts(context['id']).ranges('user').get(order='start', direction='asc')
    )
    assert_that(
        response.json,
        has_entries(
            total=2,
            items=contains_exactly(
                {'start': '100', 'end': '999'},
                {'start': '5999', 'end': '6000'},
            ),
        ),
    )

    response = (
        confd.contexts(context['id'])
        .ranges('user')
        .get(order='start', direction='desc')
    )
    assert_that(
        response.json,
        has_entries(
            total=2,
            items=contains_exactly(
                {'start': '5999', 'end': '6000'},
                {'start': '100', 'end': '999'},
            ),
        ),
    )

    response = (
        confd.contexts(context['id']).ranges('user').get(order='end', direction='asc')
    )
    assert_that(
        response.json,
        has_entries(
            total=2,
            items=contains_exactly(
                {'start': '5999', 'end': '6000'},
                {'start': '100', 'end': '999'},
            ),
        ),
    )


@fixtures.context()
def test_search_errors(context):
    fake_context_range = confd.contexts(999999).ranges('user').get
    s.check_resource_not_found(fake_context_range, 'Context')

    response = confd.contexts(context['id']).ranges('unknown').get()
    response.assert_status(404)


@fixtures.context(wazo_tenant=MAIN_TENANT)
@fixtures.context(wazo_tenant=SUB_TENANT)
def test_search_multi_tenant(main, sub):
    response = confd.contexts(main['id']).ranges('user').get(wazo_tenant=MAIN_TENANT)
    response.assert_status(200)

    response = confd.contexts(main['id']).ranges('user').get(wazo_tenant=SUB_TENANT)
    response.assert_status(404)

    response = confd.contexts(sub['id']).ranges('user').get(wazo_tenant=MAIN_TENANT)
    response.assert_status(200)

    response = confd.contexts(sub['id']).ranges('user').get(wazo_tenant=SUB_TENANT)
    response.assert_status(200)
