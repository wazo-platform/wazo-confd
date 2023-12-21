# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_inanyorder, empty, has_entries, has_length

from ..helpers import associations as a
from ..helpers import fixtures
from ..helpers.config import CREATED_TENANT, DELETED_TENANT
from . import BaseIntegrationTest, confd, db


@fixtures.context(wazo_tenant=DELETED_TENANT)
@fixtures.user(wazo_tenant=DELETED_TENANT)
def test_remove_user_with_voicemail(deleted_ctx, user):
    with fixtures.voicemail(context=deleted_ctx['name']) as voicemail:
        with a.user_voicemail(user, voicemail, check=False):
            with BaseIntegrationTest.delete_auth_tenant(DELETED_TENANT):
                BaseIntegrationTest.sync_db()

            response = confd.users(user['uuid']).get()
            response.assert_status(404)

            response = confd.voicemails(voicemail['id']).get()
            response.assert_status(404)


@fixtures.context(wazo_tenant=DELETED_TENANT)
@fixtures.user(wazo_tenant=DELETED_TENANT)
def test_remove_user_with_line(context, user):
    with fixtures.line_sip(context=context, wazo_tenant=DELETED_TENANT) as line:
        with a.user_line(user, line, check=False):
            with BaseIntegrationTest.delete_auth_tenant(DELETED_TENANT):
                BaseIntegrationTest.sync_db()

                response = confd.users(user['uuid']).get()
                response.assert_status(404)

                response = confd.lines(line['id']).get()
                response.assert_status(404)


def test_create_default_templates_when_not_exist():
    transport_udp = confd.sip.transports.get(name='transport-udp').items[0]
    transport_wss = confd.sip.transports.get(name='transport-wss').items[0]
    response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
    assert_that(response.items, empty())

    with BaseIntegrationTest.create_auth_tenant(CREATED_TENANT):
        BaseIntegrationTest.sync_db()
        response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
        assert_that(
            response.items,
            contains_inanyorder(
                has_entries(
                    label='global',
                    transport=has_entries(uuid=transport_udp['uuid']),
                ),
                has_entries(
                    label='webrtc',
                    transport=has_entries(uuid=transport_wss['uuid']),
                ),
                has_entries(label='meeting_guest'),
                has_entries(label='registration_trunk'),
                has_entries(label='twilio_trunk'),
            ),
        )


def test_no_create_default_templates_when_exist():
    with BaseIntegrationTest.create_auth_tenant(CREATED_TENANT):
        BaseIntegrationTest.sync_db()
        response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
        assert_that(response.items, has_length(5))
        uuid_1 = response.items[0]['uuid']
        uuid_2 = response.items[1]['uuid']
        uuid_3 = response.items[2]['uuid']
        uuid_4 = response.items[3]['uuid']
        uuid_5 = response.items[4]['uuid']

        BaseIntegrationTest.sync_db()

        response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
        assert_that(
            response.items,
            contains_inanyorder(
                has_entries(uuid=uuid_1),
                has_entries(uuid=uuid_2),
                has_entries(uuid=uuid_3),
                has_entries(uuid=uuid_4),
                has_entries(uuid=uuid_5),
            ),
        )


def test_not_reset_default_templates_when_exist():
    with BaseIntegrationTest.create_auth_tenant(CREATED_TENANT):
        BaseIntegrationTest.sync_db()
        response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
        assert_that(response.items, has_length(5))
        uuid_1 = response.items[0]['uuid']

        response = confd.endpoints.sip.templates(uuid_1).put(
            asterisk_id='42',
            wazo_tenant=CREATED_TENANT,
        )

        BaseIntegrationTest.sync_db()

        response = confd.endpoints.sip.templates(uuid_1).get(wazo_tenant=CREATED_TENANT)
        assert_that(response.item, has_entries(asterisk_id='42'))


def test_reset_default_templates_when_toggle_sip_template_generated_bool():
    with BaseIntegrationTest.create_auth_tenant(CREATED_TENANT):
        BaseIntegrationTest.sync_db()
        response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
        assert_that(response.items, has_length(5))
        uuid_1 = response.items[0]['uuid']

        response = confd.endpoints.sip.templates(uuid_1).put(
            asterisk_id='42',
            wazo_tenant=CREATED_TENANT,
        )

        with db.queries() as queries:
            queries.toggle_sip_templates_generated(CREATED_TENANT, generated=False)

        BaseIntegrationTest.sync_db()

        response = confd.endpoints.sip.templates(uuid_1).get(wazo_tenant=CREATED_TENANT)
        assert_that(response.item, has_entries(asterisk_id=None))
