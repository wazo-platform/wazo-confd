# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    all_of,
    has_entries,
    has_items,
    not_,
)

from . import confd
from ..helpers import fixtures
from ..helpers.config import SUB_TENANT


@fixtures.user(subscription_type=8)
@fixtures.user(subscription_type=8)
@fixtures.user(subscription_type=9)
def test_get_user_subscription(*_):
    response = confd.users.subscriptions.get()
    assert_that(
        response.items,
        has_items(
            has_entries({'id': 8, 'count': 2}),
            has_entries({'id': 9, 'count': 1}),
        ),
    )


@fixtures.user(subscription_type=8, wazo_tenant=SUB_TENANT)
@fixtures.user(subscription_type=8)
@fixtures.user(subscription_type=9)
def test_get_user_subscription_multi_tenant(*_):
    response = confd.users.subscriptions.get(wazo_tenant=SUB_TENANT)
    assert_that(
        response.items,
        all_of(
            has_items(has_entries({'id': 8, 'count': 1})),
            not_(has_items(has_entries({'id': 9}))),
        ),
    )
