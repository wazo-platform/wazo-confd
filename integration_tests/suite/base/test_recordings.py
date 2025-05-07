# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import has_entries

from ..helpers import fixtures
from ..helpers.bus import BusClient
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd


def test_get_default():
    response = confd.recordings.announcements.get()
    assert response.item == {'recording_start': None, 'recording_stop': None}


@fixtures.user()
def test_put(user):
    bus_events = BusClient.accumulator(
        headers={'name': 'recordings_announcements_edited'}
    )

    # Set recording start/stop announcements
    result = confd.recordings.announcements.put(
        {'recording_start': 'beep', 'recording_stop': 'tt-monkeys'}
    )

    result.assert_status(204)

    bus_events.until_assert_that_accumulate(
        {
            'headers': has_entries(
                {
                    'name': 'recordings_announcements_edited',
                    'tenant_uuid': MAIN_TENANT,
                }
            ),
            'message': {
                'recording_start': 'beep',
                'recording_stop': 'tt-monkeys',
            },
        }
    )
    response = confd.recordings.announcements.get()
    assert response.item == {'recording_start': 'beep', 'recording_stop': 'tt-monkeys'}

    # Omit announcements = no changes
    result = confd.recordings.announcements.put({})

    result.assert_status(204)

    response = confd.recordings.announcements.get()
    assert response.item == {'recording_start': 'beep', 'recording_stop': 'tt-monkeys'}

    # Unset recordings announcements
    result = confd.recordings.announcements.put(
        {'recording_start': None, 'recording_stop': None}
    )

    result.assert_status(204)

    bus_events.until_assert_that_accumulate(
        {
            'headers': has_entries(
                {
                    'name': 'recordings_announcements_edited',
                    'tenant_uuid': MAIN_TENANT,
                }
            ),
            'message': {
                'recording_start': None,
                'recording_stop': None,
            },
        }
    )
    response = confd.recordings.announcements.get()
    assert response.item == {'recording_start': None, 'recording_stop': None}


def test_tenant_isolation():
    tenant_uuid_1 = MAIN_TENANT
    tenant_uuid_2 = SUB_TENANT

    confd.recordings.announcements.put(
        {'recording_start': 'test', 'recording_stop': 'beep'}, wazo_tenant=tenant_uuid_1
    )
    confd.recordings.announcements.put(
        {'recording_start': 'tt-monkeys', 'recording_stop': 'test2'},
        wazo_tenant=tenant_uuid_2,
    )

    result_1 = confd.recordings.announcements.get(wazo_tenant=tenant_uuid_1)
    result_2 = confd.recordings.announcements.get(wazo_tenant=tenant_uuid_2)

    assert result_1.item == {'recording_start': 'test', 'recording_stop': 'beep'}
    assert result_2.item == {'recording_start': 'tt-monkeys', 'recording_stop': 'test2'}


def test_put_errors():
    # invalid recording name
    result = confd.recordings.announcements.put({'recording_start': 123})
    result.assert_match(400, re.compile(re.escape('recording_start')))
    result = confd.recordings.announcements.put({'recording_stop': 123})
    result.assert_match(400, re.compile(re.escape('recording_stop')))
