# Copyright 2020-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from hamcrest import (
    assert_that,
    calling,
    contains_inanyorder,
    has_entries,
    has_properties,
    empty,
    raises,
    starts_with,
)

from wazo_provd_client.exceptions import ProvdError
from wazo_test_helpers import until

from . import BaseIntegrationTest, confd, provd
from ..helpers import associations, fixtures
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


@unittest.skip
@fixtures.context(name='deleted_ctx', wazo_tenant=DELETED_TENANT)
@fixtures.user(wazo_tenant=DELETED_TENANT)
@fixtures.line(context='deleted_ctx', wazo_tenant=DELETED_TENANT)
@fixtures.sip(wazo_tenant=DELETED_TENANT)
@fixtures.extension(context='deleted_ctx', wazo_tenant=DELETED_TENANT)
@fixtures.device(wazo_tenant=DELETED_TENANT)
def test_delete_device_when_deleting_tenant(_, user, line, sip, extension, device):
    # This test only uses provd for getting the device. Why? Because confd does not expose
    # the `config` field and we need it.
    with associations.line_endpoint_sip(line, sip, check=False), associations.user_line(
        user, line, check=False
    ), associations.line_extension(
        line, extension, check=False
    ), associations.line_device(
        line, device, check=False
    ):
        device_provd = provd.devices.get(device['id'])
        config = provd.configs.get(device_provd['config'])

        with BaseIntegrationTest.delete_auth_tenant(DELETED_TENANT):
            BusClientHeaders.send_tenant_deleted(DELETED_TENANT, 'slug3')

        def device_deleted():
            assert_that(
                calling(provd.devices.get).with_args(device['id']),
                raises(ProvdError, matching=has_properties(status_code=404)),
            )
            assert_that(
                calling(provd.configs.get).with_args(config['id']),
                raises(ProvdError, matching=has_properties(status_code=404)),
            )

        until.assert_(device_deleted, tries=5)
