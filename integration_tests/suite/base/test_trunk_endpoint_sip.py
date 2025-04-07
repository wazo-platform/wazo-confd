# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains, has_entries

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd

FAKE_ID = 999999999
FAKE_UUID = '99999999-9999-4999-9999-999999999999'


@fixtures.trunk()
@fixtures.sip()
def test_associate_errors(trunk, sip):
    fake_trunk = confd.trunks(FAKE_ID).endpoints.sip(sip['uuid']).put
    fake_sip = confd.trunks(trunk['id']).endpoints.sip(FAKE_UUID).put

    s.check_resource_not_found(fake_trunk, 'Trunk')
    s.check_resource_not_found(fake_sip, 'SIPEndpoint')


@fixtures.trunk()
@fixtures.sip()
def test_dissociate_errors(trunk, sip):
    fake_trunk = confd.trunks(FAKE_ID).endpoints.sip(sip['uuid']).delete
    fake_sip = confd.trunks(trunk['id']).endpoints.sip(FAKE_UUID).delete

    s.check_resource_not_found(fake_trunk, 'Trunk')
    s.check_resource_not_found(fake_sip, 'SIPEndpoint')


@fixtures.trunk()
@fixtures.sip()
def test_associate(trunk, sip):
    response = confd.trunks(trunk['id']).endpoints.sip(sip['uuid']).put()
    response.assert_updated()


@fixtures.trunk()
@fixtures.sip()
def test_associate_already_associated(trunk, sip):
    with a.trunk_endpoint_sip(trunk, sip):
        response = confd.trunks(trunk['id']).endpoints.sip(sip['uuid']).put()
        response.assert_updated()


@fixtures.trunk()
@fixtures.sip()
@fixtures.sip()
def test_associate_multiple_sip_to_trunk(trunk, sip1, sip2):
    with a.trunk_endpoint_sip(trunk, sip1):
        response = confd.trunks(trunk['id']).endpoints.sip(sip2['uuid']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.trunk()
@fixtures.sip()
def test_associate_multiple_trunks_to_sip(trunk1, trunk2, sip):
    with a.trunk_endpoint_sip(trunk1, sip):
        response = confd.trunks(trunk2['id']).endpoints.sip(sip['uuid']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.line()
@fixtures.sip()
def test_associate_when_line_already_associated(trunk, line, sip):
    with a.line_endpoint_sip(line, sip):
        response = confd.trunks(trunk['id']).endpoints.sip(sip['uuid']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.trunk()
@fixtures.sip()
@fixtures.register_iax()
def test_associate_when_register_iax(trunk, sip, register):
    with a.trunk_register_iax(trunk, register):
        response = confd.trunks(trunk['id']).endpoints.sip(sip['uuid']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'IAXRegister'))


@fixtures.trunk(wazo_tenant=MAIN_TENANT)
@fixtures.trunk(wazo_tenant=SUB_TENANT)
@fixtures.sip(wazo_tenant=MAIN_TENANT)
@fixtures.sip(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_trunk, sub_trunk, main_sip, sub_sip):
    response = (
        confd.trunks(main_trunk['id'])
        .endpoints.sip(sub_sip['uuid'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Trunk'))

    response = (
        confd.trunks(sub_trunk['id'])
        .endpoints.sip(main_sip['uuid'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('SIPEndpoint'))

    response = (
        confd.trunks(main_trunk['id'])
        .endpoints.sip(sub_sip['uuid'])
        .put(wazo_tenant=MAIN_TENANT)
    )
    response.assert_match(400, e.different_tenant())


@fixtures.trunk()
@fixtures.sip()
def test_dissociate(trunk, sip):
    with a.trunk_endpoint_sip(trunk, sip, check=False):
        response = confd.trunks(trunk['id']).endpoints.sip(sip['uuid']).delete()
        response.assert_deleted()


@fixtures.trunk()
@fixtures.sip()
def test_dissociate_not_associated(trunk, sip):
    response = confd.trunks(trunk['id']).endpoints.sip(sip['uuid']).delete()
    response.assert_deleted()


@fixtures.trunk(wazo_tenant=MAIN_TENANT)
@fixtures.trunk(wazo_tenant=SUB_TENANT)
@fixtures.sip(wazo_tenant=MAIN_TENANT)
@fixtures.sip(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(main_trunk, sub_trunk, main_sip, sub_sip):
    response = (
        confd.trunks(main_trunk['id'])
        .endpoints.sip(sub_sip['uuid'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Trunk'))

    response = (
        confd.trunks(sub_trunk['id'])
        .endpoints.sip(main_sip['uuid'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('SIPEndpoint'))


@fixtures.trunk()
@fixtures.sip(
    label='label',
    name='label',
    auth_section_options=[['username', 'my-username'], ['password', 'my-password']],
    registration_section_options=[['client_uri', 'client-uri']],
)
def test_get_endpoint_sip_relation(trunk, sip):
    with a.trunk_endpoint_sip(trunk, sip):
        response = confd.trunks(trunk['id']).get()
        assert_that(
            response.item,
            has_entries(
                endpoint_sip=has_entries(
                    uuid=sip['uuid'],
                    label='label',
                    name='label',
                    auth_section_options=contains(
                        contains('username', 'my-username'),
                    ),
                    registration_section_options=contains(
                        contains('client_uri', 'client-uri'),
                    ),
                )
            ),
        )


@fixtures.trunk()
@fixtures.sip()
def test_get_trunk_relation(trunk, sip):
    with a.trunk_endpoint_sip(trunk, sip):
        response = confd.endpoints.sip(sip['uuid']).get()
        assert_that(response.item, has_entries(trunk=has_entries(id=trunk['id'])))


@fixtures.trunk()
@fixtures.sip()
def test_delete_trunk_when_trunk_and_endpoint_associated(trunk, sip):
    with a.trunk_endpoint_sip(trunk, sip, check=False):
        confd.trunks(trunk['id']).delete().assert_deleted()

        deleted_trunk = confd.trunks(trunk['id']).get
        deleted_sip = confd.endpoints.sip(sip['uuid']).get
        s.check_resource_not_found(deleted_trunk, 'Trunk')
        s.check_resource_not_found(deleted_sip, 'SIPEndpoint')


@fixtures.trunk()
@fixtures.sip()
def test_delete_sip_when_trunk_and_sip_associated(trunk, sip):
    with a.trunk_endpoint_sip(trunk, sip, check=False):
        confd.endpoints.sip(sip['uuid']).delete().assert_deleted()

        response = confd.trunks(trunk['id']).get()
        assert_that(response.item, has_entries(endpoint_sip=None))


@fixtures.trunk()
@fixtures.sip()
def test_bus_events(trunk, sip):
    url = confd.trunks(trunk['id']).endpoints.sip(sip['uuid'])
    headers = {'tenant_uuid': trunk['tenant_uuid']}

    s.check_event('trunk_endpoint_sip_associated', headers, url.put)
    s.check_event('trunk_endpoint_sip_dissociated', headers, url.delete)
