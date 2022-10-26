# Copyright 2020-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    has_entries,
    has_items,
    has_key,
    not_,
)
from ..helpers import errors as e, fixtures
from ..helpers.config import MAIN_TENANT, SUB_TENANT

from . import confd


def test_get():
    response = confd.tenants(MAIN_TENANT).get()
    assert_that(
        response.item,
        all_of(
            has_entries(uuid=MAIN_TENANT),
            has_key('sip_templates_generated'),
            has_key('global_sip_template_uuid'),
            has_key('webrtc_sip_template_uuid'),
            has_key('registration_trunk_sip_template_uuid'),
        ),
    )


@fixtures.trunk(wazo_tenant=SUB_TENANT)  # Note: This creates the tenant in the DB
def test_get_multi_tenant(_):
    response = confd.tenants(MAIN_TENANT).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Tenant'))

    response = confd.tenants(SUB_TENANT).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(uuid=SUB_TENANT))


@fixtures.trunk(wazo_tenant=SUB_TENANT)  # Note: This creates the tenant in the DB
def test_list_multi_tenant(_):
    response = confd.tenants.get(wazo_tenant=MAIN_TENANT)
    assert_that(
        response.items,
        all_of(
            has_items(has_entries(uuid=MAIN_TENANT)),
            not_(has_items(has_entries(uuid=SUB_TENANT))),
        ),
    )

    response = confd.tenants.get(wazo_tenant=SUB_TENANT)
    assert_that(
        response.items,
        all_of(
            has_items(has_entries(uuid=SUB_TENANT)),
            not_(has_items(has_entries(uuid=MAIN_TENANT))),
        ),
    )

    response = confd.tenants.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(
        response.items,
        has_items(has_entries(uuid=MAIN_TENANT), has_entries(uuid=SUB_TENANT)),
    )
