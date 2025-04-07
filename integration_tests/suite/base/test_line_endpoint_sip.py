# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    has_entries,
    has_items,
    none,
)
from wazo_test_helpers.hamcrest.uuid_ import uuid_

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import CONTEXT, MAIN_TENANT, SUB_TENANT
from . import confd

FAKE_UUID = '99999999-9999-4999-9999-999999999999'
FAKE_ID = 999999999


@fixtures.line()
@fixtures.sip()
def test_associate_errors(line, sip):
    fake_line = confd.lines(FAKE_ID).endpoints.sip(sip['uuid']).put
    fake_sip = confd.lines(line['id']).endpoints.sip(FAKE_UUID).put

    s.check_resource_not_found(fake_line, 'Line')
    s.check_resource_not_found(fake_sip, 'SIPEndpoint')


@fixtures.line()
@fixtures.sip()
def test_dissociate_errors(line, sip):
    fake_line = confd.lines(FAKE_ID).endpoints.sip(sip['uuid']).delete
    fake_sip = confd.lines(line['id']).endpoints.sip(FAKE_UUID).delete

    s.check_resource_not_found(fake_line, 'Line')
    s.check_resource_not_found(fake_sip, 'SIPEndpoint')


@fixtures.line()
@fixtures.sip()
def test_associate(line, sip):
    response = confd.lines(line['id']).endpoints.sip(sip['uuid']).put()
    response.assert_updated()


@fixtures.line()
@fixtures.sip()
def test_associate_when_endpoint_already_associated(line, sip):
    with a.line_endpoint_sip(line, sip):
        response = confd.lines(line['id']).endpoints.sip(sip['uuid']).put()
        response.assert_updated()


@fixtures.line()
@fixtures.sip_template()
def test_associate_with_sip_template(line, sip_template):
    response = confd.lines(line['id']).endpoints.sip(sip_template['uuid']).put()
    response.assert_match(404, e.not_found('SIPEndpoint'))


@fixtures.line()
@fixtures.sip()
@fixtures.sip()
def test_associate_with_another_endpoint_when_already_associated(line, sip1, sip2):
    with a.line_endpoint_sip(line, sip1):
        response = confd.lines(line['id']).endpoints.sip(sip2['uuid']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.line()
@fixtures.line()
@fixtures.sip()
def test_associate_multiple_lines_to_sip(line1, line2, sip):
    with a.line_endpoint_sip(line1, sip):
        response = confd.lines(line2['id']).endpoints.sip(sip['uuid']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.line()
@fixtures.trunk()
@fixtures.sip()
def test_associate_when_trunk_already_associated(line, trunk, sip):
    with a.trunk_endpoint_sip(trunk, sip):
        response = confd.lines(line['id']).endpoints.sip(sip['uuid']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.context(wazo_tenant=MAIN_TENANT, label='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, label='sub-internal')
@fixtures.sip(wazo_tenant=MAIN_TENANT)
@fixtures.sip(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_ctx, sub_ctx, main_sip, sub_sip):
    @fixtures.line(context=main_ctx['name'])
    @fixtures.line(context=sub_ctx['name'])
    def aux(main_line, sub_line):
        response = (
            confd.lines(main_line['id'])
            .endpoints.sip(sub_sip['uuid'])
            .put(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Line'))

        response = (
            confd.lines(sub_line['id'])
            .endpoints.sip(main_sip['uuid'])
            .put(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('SIPEndpoint'))

        response = (
            confd.lines(main_line['id'])
            .endpoints.sip(sub_sip['uuid'])
            .put(wazo_tenant=MAIN_TENANT)
        )
        response.assert_match(400, e.different_tenant())

    aux()


@fixtures.line()
@fixtures.sip()
def test_dissociate(line, sip):
    with a.line_endpoint_sip(line, sip, check=False):
        response = confd.lines(line['id']).endpoints.sip(sip['uuid']).delete()
        response.assert_deleted()


@fixtures.line()
@fixtures.sip()
def test_dissociate_when_not_associated(line, sip):
    response = confd.lines(line['id']).endpoints.sip(sip['uuid']).delete()
    response.assert_deleted()


@fixtures.line()
@fixtures.sip()
@fixtures.user()
def test_dissociate_when_associated_to_user(line, sip, user):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line):
        response = confd.lines(line['id']).endpoints.sip(sip['uuid']).delete()
        response.assert_match(400, e.resource_associated('Line', 'User'))


@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_dissociate_when_associated_to_extension(line, sip, extension):
    with a.line_endpoint_sip(line, sip), a.line_extension(line, extension):
        response = confd.lines(line['id']).endpoints.sip(sip['uuid']).delete()
        response.assert_match(400, e.resource_associated('Line', 'Extension'))


@fixtures.context(wazo_tenant=MAIN_TENANT, label='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, label='sub-internal')
@fixtures.sip(wazo_tenant=MAIN_TENANT)
@fixtures.sip(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(main_ctx, sub_ctx, main_sip, sub_sip):
    @fixtures.line(context=main_ctx['name'])
    @fixtures.line(context=sub_ctx['name'])
    def aux(main_line, sub_line):
        response = (
            confd.lines(main_line['id'])
            .endpoints.sip(sub_sip['uuid'])
            .delete(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Line'))

        response = (
            confd.lines(sub_line['id'])
            .endpoints.sip(main_sip['uuid'])
            .delete(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('SIPEndpoint'))

    aux()


@fixtures.line()
@fixtures.sip(
    label='my-endpoint',
    name='my-endpoint',
    auth_section_options=[['username', 'my-username'], ['password', 'my-password']],
)
def test_get_endpoint_sip_relation(line, sip):
    with a.line_endpoint_sip(line, sip):
        response = confd.lines(line['id']).get()
        assert_that(
            response.item,
            has_entries(
                endpoint_sip=has_entries(
                    uuid=sip['uuid'],
                    label='my-endpoint',
                    name='my-endpoint',
                    auth_section_options=contains_inanyorder(
                        contains('username', 'my-username'),
                    ),
                )
            ),
        )


@fixtures.line()
@fixtures.sip()
def test_get_line_relation(line, sip):
    with a.line_endpoint_sip(line, sip):
        response = confd.endpoints.sip(sip['uuid']).get()
        assert_that(response.item, has_entries(line=has_entries(id=line['id'])))


@fixtures.line()
@fixtures.sip()
def test_delete_endpoint_dissociates_line(line, sip):
    with a.line_endpoint_sip(line, sip, check=False):
        response = confd.endpoints.sip(sip['uuid']).delete()
        response.assert_deleted()

        response = confd.lines(line['id']).get()
        assert_that(response.item, has_entries(endpoint_sip=None))


@fixtures.line()
@fixtures.sip()
def test_bus_events(line, sip):
    url = confd.lines(line['id']).endpoints.sip(sip['uuid'])
    headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event('line_endpoint_sip_associated', headers, url.put)
    s.check_event('line_endpoint_sip_dissociated', headers, url.delete)


@fixtures.transport()
@fixtures.sip_template()
@fixtures.sip_template()
@fixtures.registrar()
def test_create_line_with_endpoint_sip_with_all_parameters(
    transport, template_1, template_2, registrar
):
    aor_section_options = [
        ['@custom_variable', 'custom'],
        ['qualify_frequency', '60'],
        ['maximum_expiration', '3600'],
        ['remove_existing', 'yes'],
        ['max_contacts', '1'],
    ]
    auth_section_options = [['username', 'yiq8yej0'], ['password', 'yagq7x0w']]
    endpoint_section_options = [
        ['@custom_variable', 'custom'],
        ['force_rport', 'yes'],
        ['rewrite_contact', 'yes'],
        ['callerid', '"Firstname Lastname" <100>'],
        ['context', CONTEXT],
    ]
    identify_section_options = [
        ['match', '54.172.60.0'],
        ['match', '54.172.60.1'],
        ['match', '54.172.60.2'],
    ]
    registration_section_options = [
        ['client_uri', 'sip:peer@proxy.example.com'],
        ['server_uri', 'sip:proxy.example.com'],
        ['expiration', '120'],
    ]
    registration_outbound_auth_section_options = [
        ['username', 'outbound-registration-username'],
        ['password', 'outbound-registration-password'],
    ]
    outbound_auth_section_options = [
        ['username', 'outbound-auth'],
        ['password', 'outbound-password'],
    ]

    response = confd.lines.post(
        context=CONTEXT,
        position=2,
        registrar=registrar['id'],
        provisioning_code='887865',
        endpoint_sip={
            'name': "name",
            'label': "label",
            'aor_section_options': aor_section_options,
            'auth_section_options': auth_section_options,
            'endpoint_section_options': endpoint_section_options,
            'identify_section_options': identify_section_options,
            'registration_section_options': registration_section_options,
            'registration_outbound_auth_section_options': registration_outbound_auth_section_options,
            'outbound_auth_section_options': outbound_auth_section_options,
            'transport': transport,
            'templates': [template_1, template_2],
            'asterisk_id': 'asterisk_id',
        },
    )
    line_id = response.item['id']

    try:
        assert_that(
            response.item,
            has_entries(
                context=CONTEXT,
                position=2,
                device_slot=2,
                name='name',
                protocol='sip',
                device_id=none(),
                caller_id_name='Firstname Lastname',
                caller_id_num='100',
                registrar=registrar['id'],
                provisioning_code="887865",
                provisioning_extension="887865",
                tenant_uuid=MAIN_TENANT,
                endpoint_sip=has_entries(
                    tenant_uuid=MAIN_TENANT,
                    name='name',
                    label='label',
                    aor_section_options=aor_section_options,
                    auth_section_options=auth_section_options,
                    endpoint_section_options=endpoint_section_options,
                    identify_section_options=identify_section_options,
                    registration_section_options=registration_section_options,
                    registration_outbound_auth_section_options=registration_outbound_auth_section_options,
                    outbound_auth_section_options=outbound_auth_section_options,
                    transport=has_entries(uuid=transport['uuid']),
                    templates=contains(
                        has_entries(uuid=template_1['uuid'], label=template_1['label']),
                        has_entries(uuid=template_2['uuid'], label=template_2['label']),
                    ),
                    asterisk_id='asterisk_id',
                ),
            ),
        )

        line = confd.lines(line_id).get().item
        assert_that(
            line,
            has_entries(
                endpoint_sip=has_entries(
                    uuid=uuid_(),
                    name='name',
                ),
            ),
        )

        response = confd.lines(line_id).put(**line)
        response.assert_updated()
    finally:
        confd.lines(line_id).delete().assert_deleted()


def test_create_line_with_endpoint_sip_no_context():
    response = confd.lines.post(
        context=CONTEXT,
        endpoint_sip={'name': 'name'},
    )
    line_id = response.item['id']

    try:
        assert_that(
            response.item,
            has_entries(
                context=CONTEXT,
                endpoint_sip=has_entries(
                    endpoint_section_options=has_items(
                        ['context', CONTEXT],
                    ),
                ),
            ),
        )
    finally:
        confd.lines(line_id).delete().assert_deleted()
