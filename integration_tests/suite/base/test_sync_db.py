# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
    has_entries,
    has_length,
    empty,
)

from . import BaseIntegrationTest, confd, db
from ..helpers import (
    associations as a,
    fixtures,
)
from ..helpers.config import DELETED_TENANT, CREATED_TENANT


@fixtures.context(name='DELETED', wazo_tenant=DELETED_TENANT)
@fixtures.user(wazo_tenant=DELETED_TENANT)
@fixtures.voicemail(context='DELETED')
def test_remove_user_with_voicemail(_, user, voicemail):
    with a.user_voicemail(user, voicemail, check=False):
        with BaseIntegrationTest.delete_auth_tenant(DELETED_TENANT):
            BaseIntegrationTest.sync_db()

        response = confd.users(user['uuid']).get()
        response.assert_status(404)

        response = confd.voicemails(voicemail['id']).get()
        assert_that(response.item, has_entries(users=empty()))


@fixtures.context(name='DELETED', wazo_tenant=DELETED_TENANT)
@fixtures.user(wazo_tenant=DELETED_TENANT)
def test_remove_user_with_line(context, user):
    with fixtures.line_sip(context=context, wazo_tenant=DELETED_TENANT) as line:
        with a.user_line(user, line, check=False):
            with BaseIntegrationTest.delete_auth_tenant(DELETED_TENANT):
                BaseIntegrationTest.sync_db()

            response = confd.users(user['uuid']).get()
            response.assert_status(404)

            response = confd.lines(line['id']).get()
            assert_that(response.item, has_entries(users=empty()))


def test_create_default_templates_when_not_exist():
    response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
    assert_that(response.items, empty())

    with BaseIntegrationTest.create_auth_tenant(CREATED_TENANT):
        BaseIntegrationTest.sync_db()

    response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
    assert_that(
        response.items,
        contains_inanyorder(
            has_entries(label='global'),
            has_entries(label='webrtc'),
            has_entries(label='global_trunk'),
            has_entries(label='twilio_trunk'),
        ),
    )


def test_no_create_default_templates_when_exist():
    with BaseIntegrationTest.create_auth_tenant(CREATED_TENANT):
        BaseIntegrationTest.sync_db()
        response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
        assert_that(response.items, has_length(4))
        uuid_1 = response.items[0]['uuid']
        uuid_2 = response.items[1]['uuid']
        uuid_3 = response.items[2]['uuid']
        uuid_4 = response.items[3]['uuid']

        BaseIntegrationTest.sync_db()

        response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
        assert_that(
            response.items,
            contains_inanyorder(
                has_entries(uuid=uuid_1),
                has_entries(uuid=uuid_2),
                has_entries(uuid=uuid_3),
                has_entries(uuid=uuid_4),
            ),
        )


def test_not_reset_default_templates_when_exist():
    with BaseIntegrationTest.create_auth_tenant(CREATED_TENANT):
        BaseIntegrationTest.sync_db()
        response = confd.endpoints.sip.templates.get(wazo_tenant=CREATED_TENANT)
        assert_that(response.items, has_length(4))
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
        assert_that(response.items, has_length(4))
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
