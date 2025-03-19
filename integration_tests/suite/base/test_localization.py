# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re
from hamcrest import has_entries

from . import confd
from ..helpers import fixtures
from ..helpers.bus import BusClient
from ..helpers.config import MAIN_TENANT, SUB_TENANT


def test_get_default():
    response = confd.localization.get()
    assert response.item == {'country': None, 'tenant_uuid': MAIN_TENANT}


@fixtures.user()
def test_put(user):
    bus_events = BusClient.accumulator(headers={'name': 'localization_edited'})

    # Set country
    result = confd.localization.put({'country': 'CA'})

    result.assert_status(204)

    bus_events.until_assert_that_accumulate(
        {
            'headers': has_entries(
                {
                    'name': 'localization_edited',
                    'tenant_uuid': MAIN_TENANT,
                }
            ),
            'message': {
                'country': 'CA',
                'tenant_uuid': MAIN_TENANT,
            },
        }
    )
    response = confd.localization.get()
    assert response.item == {'country': 'CA', 'tenant_uuid': MAIN_TENANT}
    response = confd.users(user['uuid']).get()
    assert response.item['country'] == 'CA'

    # Omit country = no changes
    result = confd.localization.put({})

    result.assert_status(204)

    response = confd.localization.get()
    assert response.item == {'country': 'CA', 'tenant_uuid': MAIN_TENANT}
    response = confd.users(user['uuid']).get()
    assert response.item['country'] == 'CA'

    # Unset country
    result = confd.localization.put({'country': None})

    result.assert_status(204)

    bus_events.until_assert_that_accumulate(
        {
            'headers': has_entries(
                {
                    'name': 'localization_edited',
                    'tenant_uuid': MAIN_TENANT,
                }
            ),
            'message': {
                'country': None,
                'tenant_uuid': MAIN_TENANT,
            },
        }
    )
    response = confd.localization.get()
    assert response.item == {'country': None, 'tenant_uuid': MAIN_TENANT}
    response = confd.users(user['uuid']).get()
    assert response.item['country'] is None


def test_tenant_isolation():
    tenant_uuid_1 = MAIN_TENANT
    tenant_uuid_2 = SUB_TENANT

    confd.localization.put({'country': 'CA'}, wazo_tenant=tenant_uuid_1)
    confd.localization.put({'country': 'FR'}, wazo_tenant=tenant_uuid_2)

    result_1 = confd.localization.get(wazo_tenant=tenant_uuid_1)
    result_2 = confd.localization.get(wazo_tenant=tenant_uuid_2)

    assert result_1.item['country'] == 'CA'
    assert result_1.item['tenant_uuid'] == tenant_uuid_1
    assert result_2.item['country'] == 'FR'
    assert result_2.item['tenant_uuid'] == tenant_uuid_2


def test_put_errors():
    # invalid country
    result = confd.localization.put({'country': 'ZX'})
    result.assert_match(400, re.compile(re.escape('country')))
