# Copyright 2020-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
    has_entries,
    empty,
    starts_with,
)

from wazo_test_helpers import until

from . import BaseIntegrationTest, confd
from ..helpers import errors, fixtures
from ..helpers.config import CREATED_TENANT, DELETED_TENANT
from ..helpers.bus import BusClientHeaders


def test_create_default_templates_when_not_exist():
    response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
    assert_that(response.items, empty())

    with BaseIntegrationTest.create_auth_tenant(CREATED_TENANT):
        BusClientHeaders.send_tenant_created(CREATED_TENANT, 'myslug')

    def templates_created():
        response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
        assert_that(
            response.items,
            contains_inanyorder(
                has_entries(label='global'),
                has_entries(label='webrtc'),
                has_entries(label='webrtc_video'),
                has_entries(label='meeting_guest'),
                has_entries(label='registration_trunk'),
                has_entries(label='twilio_trunk'),
            ),
        )

    def slug_created():
        # There's no API to check the tenant slug. It is part of any new group name
        response = confd.groups.post({'label': 'ignore'}, wazo_tenant=CREATED_TENANT)
        assert_that(response.item, has_entries(name=starts_with('grp-myslug-')))

    until.assert_(templates_created, tries=5)
    until.assert_(slug_created, tries=5)


@fixtures.device(wazo_tenant=DELETED_TENANT)
def test_delete_device_when_deleting_tenant(device):
    response = confd.devices(device['id']).get()
    assert_that(response.item, has_entries(**device))

    with BaseIntegrationTest.delete_auth_tenant(DELETED_TENANT):
        BusClientHeaders.send_tenant_deleted(DELETED_TENANT, 'slug3')

    def device_deleted():
        response = confd.devices(device['id']).get()
        response.assert_match(404, errors.not_found('Device'))

    until.assert_(device_deleted, tries=5)
