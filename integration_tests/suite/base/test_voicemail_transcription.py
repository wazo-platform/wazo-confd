# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from ..helpers import scenarios as s
from ..helpers.bus import BusClient
from ..helpers.config import MAIN_TENANT, SUB_TENANT, TOKEN_SUB_TENANT
from . import confd


def test_get_default():
    response = confd.voicemails.transcription.get()
    assert_that(
        response.item,
        has_entries(
            {
                'enabled': False,
            }
        ),
    )


def test_put_enable():
    bus_events = BusClient.accumulator(
        headers={'name': 'voicemail_transcription_config_edited'}
    )

    body = {'enabled': True}
    result = confd.voicemails.transcription.put(body)
    result.assert_status(204)
    response = confd.voicemails.transcription.get()
    assert_that(response.item, has_entries(body))

    bus_events.until_assert_that_accumulate(
        {
            'headers': has_entries(
                {
                    'name': 'voicemail_transcription_config_edited',
                    'tenant_uuid': MAIN_TENANT,
                }
            ),
            'message': {'enabled': True},
        }
    )

    # Reset to default
    confd.voicemails.transcription.put({'enabled': False})


def test_put_disable():
    confd.voicemails.transcription.put({'enabled': True})

    bus_events = BusClient.accumulator(
        headers={'name': 'voicemail_transcription_config_edited'}
    )

    body = {'enabled': False}
    result = confd.voicemails.transcription.put(body)
    result.assert_status(204)
    response = confd.voicemails.transcription.get()
    assert_that(response.item, has_entries(body))

    bus_events.until_assert_that_accumulate(
        {
            'headers': has_entries(
                {
                    'name': 'voicemail_transcription_config_edited',
                    'tenant_uuid': MAIN_TENANT,
                }
            ),
            'message': {'enabled': False},
        }
    )


def test_put_errors():
    s.check_missing_body_returns_error(confd.voicemails.transcription, 'PUT')
    s.check_bogus_field_returns_error(
        confd.voicemails.transcription.put, 'enabled', 'not-a-bool'
    )


def test_tenant_isolation():
    # Sub-tenant should have its own default config
    response = confd.voicemails.transcription.get(
        token=TOKEN_SUB_TENANT, wazo_tenant=SUB_TENANT
    )
    assert_that(
        response.item,
        has_entries(
            {
                'enabled': False,
            }
        ),
    )

    # Enable for sub-tenant
    result = confd.voicemails.transcription.put(
        {'enabled': True}, token=TOKEN_SUB_TENANT, wazo_tenant=SUB_TENANT
    )
    result.assert_status(204)

    # Main tenant should still be disabled
    response = confd.voicemails.transcription.get()
    assert_that(response.item, has_entries({'enabled': False}))

    # Sub-tenant should be enabled
    response = confd.voicemails.transcription.get(
        token=TOKEN_SUB_TENANT, wazo_tenant=SUB_TENANT
    )
    assert_that(response.item, has_entries({'enabled': True}))

    # Reset sub-tenant
    confd.voicemails.transcription.put(
        {'enabled': False}, token=TOKEN_SUB_TENANT, wazo_tenant=SUB_TENANT
    )
