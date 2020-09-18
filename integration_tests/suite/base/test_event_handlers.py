# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
    has_entries,
    empty,
)

from xivo_test_helpers import until

from . import BaseIntegrationTest, confd
from ..helpers.config import CREATED_TENANT
from ..helpers.bus import BusClientHeaders


def test_create_default_templates_when_not_exist():
    response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
    assert_that(response.items, empty())

    with BaseIntegrationTest.create_auth_tenant(CREATED_TENANT):
        BusClientHeaders.send_tenant_created(CREATED_TENANT)

    def templates_created():
        response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
        assert_that(
            response.items,
            contains_inanyorder(
                has_entries(label='global'),
                has_entries(label='webrtc'),
                has_entries(label='webrtc_video'),
                has_entries(label='registration_trunk'),
                has_entries(label='twilio_trunk'),
            ),
        )

    until.assert_(templates_created, tries=5)
