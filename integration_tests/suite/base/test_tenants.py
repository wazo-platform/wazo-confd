# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    has_entries,
    has_items,
    has_key,
    not_,
)

from wazo_test_helpers import until

from . import confd, BaseIntegrationTest
from ..helpers import errors as e, fixtures
from ..helpers.bus import BusClient
from ..helpers.config import MAIN_TENANT, SUB_TENANT, DELETED_TENANT


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



@fixtures.user(wazo_tenant=DELETED_TENANT)
@fixtures.group(wazo_tenant=DELETED_TENANT)
@fixtures.incall(wazo_tenant=DELETED_TENANT)
@fixtures.outcall(wazo_tenant=DELETED_TENANT)
@fixtures.trunk(wazo_tenant=DELETED_TENANT)
@fixtures.conference(wazo_tenant=DELETED_TENANT)
@fixtures.context(name='mycontext', wazo_tenant=DELETED_TENANT)
@fixtures.voicemail(context='mycontext', wazo_tenant=DELETED_TENANT)
def test_delete_tenant_by_event(
    user, group, incall, outcall, trunk, conference, context, voicemail
):
    BusClient.send_tenant_deleted(DELETED_TENANT, 'slug2')

    def tenant_deleted():
        response = confd.tenants(DELETED_TENANT).get(wazo_tenant=MAIN_TENANT)
        response.assert_match(404, e.not_found(resource='Tenant'))

        response = confd.users(user['uuid']).get()
        response.assert_status(404)

        response = confd.groups(group['uuid']).get()
        response.assert_status(404)

        response = confd.incalls(incall['id']).get()
        response.assert_status(404)

        response = confd.outcalls(outcall['id']).get()
        response.assert_status(404)

        response = confd.trunks(trunk['id']).get()
        response.assert_status(404)

        response = confd.conferences(conference['id']).get()
        response.assert_status(404)

        response = confd.context(context['id']).get()
        response.assert_status(404)

        response = confd.voicemails(voicemail['id']).get()
        response.assert_status(404)

    until.assert_(tenant_deleted, tries=5, interval=5)


@fixtures.user(wazo_tenant=DELETED_TENANT)
@fixtures.group(wazo_tenant=DELETED_TENANT)
@fixtures.incall(wazo_tenant=DELETED_TENANT)
@fixtures.outcall(wazo_tenant=DELETED_TENANT)
@fixtures.trunk(wazo_tenant=DELETED_TENANT)
@fixtures.conference(wazo_tenant=DELETED_TENANT)
@fixtures.context(name='mycontext', wazo_tenant=DELETED_TENANT)
@fixtures.voicemail(context='mycontext', wazo_tenant=DELETED_TENANT)
def test_delete_tenant_by_sync_db(
    user, group, incall, outcall, trunk, conference, context, voicemail
):

    with BaseIntegrationTest.delete_auth_tenant(DELETED_TENANT):
        BaseIntegrationTest.sync_db()

        def tenant_deleted():
            response = confd.tenants(DELETED_TENANT).get(wazo_tenant=MAIN_TENANT)
            response.assert_match(404, e.not_found(resource='Tenant'))

            response = confd.users(user['uuid']).get()
            response.assert_status(404)

            response = confd.groups(group['uuid']).get()
            response.assert_status(404)

            response = confd.incalls(incall['id']).get()
            response.assert_status(404)

            response = confd.outcalls(outcall['id']).get()
            response.assert_status(404)

            response = confd.trunks(trunk['id']).get()
            response.assert_status(404)

            response = confd.conferences(conference['id']).get()
            response.assert_status(404)

            response = confd.context(context['id']).get()
            response.assert_status(404)

            response = confd.voicemails(voicemail['id']).get()
            response.assert_status(404)

        until.assert_(tenant_deleted, tries=5, interval=5)
