# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries, none

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd

FAKE_ID = 999999999


@fixtures.trunk()
@fixtures.iax()
def test_associate_errors(trunk, iax):
    fake_trunk = confd.trunks(FAKE_ID).endpoints.iax(iax['id']).put
    fake_iax = confd.trunks(trunk['id']).endpoints.iax(FAKE_ID).put

    s.check_resource_not_found(fake_trunk, 'Trunk')
    s.check_resource_not_found(fake_iax, 'IAXEndpoint')


@fixtures.trunk()
@fixtures.iax()
def test_dissociate_errors(trunk, iax):
    fake_trunk = confd.trunks(FAKE_ID).endpoints.iax(iax['id']).delete
    fake_iax = confd.trunks(trunk['id']).endpoints.iax(FAKE_ID).delete

    s.check_resource_not_found(fake_trunk, 'Trunk')
    s.check_resource_not_found(fake_iax, 'IAXEndpoint')


@fixtures.trunk()
@fixtures.iax()
def test_associate(trunk, iax):
    response = confd.trunks(trunk['id']).endpoints.iax(iax['id']).put()
    response.assert_updated()


@fixtures.trunk()
@fixtures.iax()
def test_associate_already_associated(trunk, iax):
    with a.trunk_endpoint_iax(trunk, iax):
        response = confd.trunks(trunk['id']).endpoints.iax(iax['id']).put()
        response.assert_updated()


@fixtures.trunk()
@fixtures.iax()
@fixtures.iax()
def test_associate_multiple_iax_to_trunk(trunk, iax1, iax2):
    with a.trunk_endpoint_iax(trunk, iax1):
        response = confd.trunks(trunk['id']).endpoints.iax(iax2['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.trunk()
@fixtures.iax()
def test_associate_multiple_trunks_to_iax(trunk1, trunk2, iax):
    with a.trunk_endpoint_iax(trunk1, iax):
        response = confd.trunks(trunk2['id']).endpoints.iax(iax['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk(wazo_tenant=MAIN_TENANT)
@fixtures.trunk(wazo_tenant=SUB_TENANT)
@fixtures.iax(wazo_tenant=MAIN_TENANT)
@fixtures.iax(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_trunk, sub_trunk, main_iax, sub_iax):
    response = (
        confd.trunks(main_trunk['id'])
        .endpoints.iax(sub_iax['id'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Trunk'))

    response = (
        confd.trunks(sub_trunk['id'])
        .endpoints.iax(main_iax['id'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('IAXEndpoint'))

    response = (
        confd.trunks(main_trunk['id'])
        .endpoints.iax(sub_iax['id'])
        .put(wazo_tenant=MAIN_TENANT)
    )
    response.assert_match(400, e.different_tenant())


@fixtures.trunk()
@fixtures.iax()
def test_dissociate(trunk, iax):
    with a.trunk_endpoint_iax(trunk, iax, check=False):
        response = confd.trunks(trunk['id']).endpoints.iax(iax['id']).delete()
        response.assert_deleted()


@fixtures.trunk()
@fixtures.iax()
def test_dissociate_not_associated(trunk, iax):
    response = confd.trunks(trunk['id']).endpoints.iax(iax['id']).delete()
    response.assert_deleted()


@fixtures.trunk(wazo_tenant=MAIN_TENANT)
@fixtures.trunk(wazo_tenant=SUB_TENANT)
@fixtures.iax(wazo_tenant=MAIN_TENANT)
@fixtures.iax(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(main_trunk, sub_trunk, main_iax, sub_iax):
    response = (
        confd.trunks(main_trunk['id'])
        .endpoints.iax(sub_iax['id'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Trunk'))

    response = (
        confd.trunks(sub_trunk['id'])
        .endpoints.iax(main_iax['id'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('IAXEndpoint'))


@fixtures.trunk()
@fixtures.iax()
def test_get_endpoint_iax_relation(trunk, iax):
    with a.trunk_endpoint_iax(trunk, iax):
        response = confd.trunks(trunk['id']).get()
        assert_that(
            response.item,
            has_entries(endpoint_iax=has_entries(id=iax['id'], name=iax['name'])),
        )


@fixtures.trunk()
@fixtures.iax()
def test_get_trunk_relation(trunk, iax):
    with a.trunk_endpoint_iax(trunk, iax):
        response = confd.endpoints.iax(iax['id']).get()
        assert_that(response.item, has_entries(trunk=has_entries(id=trunk['id'])))


@fixtures.trunk()
@fixtures.iax()
def test_delete_trunk_when_trunk_and_endpoint_associated(trunk, iax):
    with a.trunk_endpoint_iax(trunk, iax, check=False):
        confd.trunks(trunk['id']).delete().assert_deleted()

        deleted_trunk = confd.trunks(trunk['id']).get
        deleted_iax = confd.endpoints.iax(iax['id']).get
        s.check_resource_not_found(deleted_trunk, 'Trunk')
        s.check_resource_not_found(deleted_iax, 'IAXEndpoint')


@fixtures.trunk()
@fixtures.iax()
def test_delete_iax_when_trunk_and_iax_associated(trunk, iax):
    with a.trunk_endpoint_iax(trunk, iax, check=False):
        confd.endpoints.iax(iax['id']).delete().assert_deleted()

        response = confd.trunks(trunk['id']).get()
        assert_that(response.item, has_entries(endpoint_iax=none()))


@fixtures.trunk()
@fixtures.iax()
def test_bus_events(trunk, iax):
    url = confd.trunks(trunk['id']).endpoints.iax(iax['id'])
    headers = {'tenant_uuid': trunk['tenant_uuid']}

    s.check_event('trunk_endpoint_iax_associated', headers, url.put)
    s.check_event('trunk_endpoint_iax_dissociated', headers, url.delete)
