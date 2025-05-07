# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd

FAKE_ID = 999999999


@fixtures.trunk()
@fixtures.custom()
def test_associate_errors(trunk, custom):
    fake_trunk = confd.trunks(FAKE_ID).endpoints.custom(custom['id']).put
    fake_custom = confd.trunks(trunk['id']).endpoints.custom(FAKE_ID).put

    s.check_resource_not_found(fake_trunk, 'Trunk')
    s.check_resource_not_found(fake_custom, 'CustomEndpoint')


@fixtures.trunk()
@fixtures.custom()
def test_dissociate_errors(trunk, custom):
    fake_trunk = confd.trunks(FAKE_ID).endpoints.custom(custom['id']).delete
    fake_custom = confd.trunks(trunk['id']).endpoints.custom(FAKE_ID).delete

    s.check_resource_not_found(fake_trunk, 'Trunk')
    s.check_resource_not_found(fake_custom, 'CustomEndpoint')


@fixtures.trunk()
@fixtures.custom()
def test_associate(trunk, custom):
    response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).put()
    response.assert_updated()


@fixtures.trunk()
@fixtures.custom()
def test_associate_already_associated(trunk, custom):
    with a.trunk_endpoint_custom(trunk, custom):
        response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).put()
        response.assert_updated()


@fixtures.trunk()
@fixtures.custom()
@fixtures.custom()
def test_associate_multiple_custom_to_trunk(trunk, custom1, custom2):
    with a.trunk_endpoint_custom(trunk, custom1):
        response = confd.trunks(trunk['id']).endpoints.custom(custom2['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.trunk()
@fixtures.custom()
def test_associate_multiple_trunks_to_custom(trunk1, trunk2, custom):
    with a.trunk_endpoint_custom(trunk1, custom):
        response = confd.trunks(trunk2['id']).endpoints.custom(custom['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.line()
@fixtures.custom()
def test_associate_when_line_already_associated(trunk, line, custom):
    with a.line_endpoint_custom(line, custom):
        response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.trunk()
@fixtures.custom()
@fixtures.register_iax()
def test_associate_when_register_iax(trunk, custom, register):
    with a.trunk_register_iax(trunk, register):
        response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'IAXRegister'))


@fixtures.trunk(wazo_tenant=MAIN_TENANT)
@fixtures.trunk(wazo_tenant=SUB_TENANT)
@fixtures.custom(wazo_tenant=MAIN_TENANT)
@fixtures.custom(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_trunk, sub_trunk, main_custom, sub_custom):
    response = (
        confd.trunks(main_trunk['id'])
        .endpoints.custom(sub_custom['id'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Trunk'))

    response = (
        confd.trunks(sub_trunk['id'])
        .endpoints.custom(main_custom['id'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('CustomEndpoint'))

    response = (
        confd.trunks(main_trunk['id'])
        .endpoints.custom(sub_custom['id'])
        .put(wazo_tenant=MAIN_TENANT)
    )
    response.assert_match(400, e.different_tenant())


@fixtures.trunk()
@fixtures.custom()
def test_dissociate(trunk, custom):
    with a.trunk_endpoint_custom(trunk, custom, check=False):
        response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).delete()
        response.assert_deleted()


@fixtures.trunk()
@fixtures.custom()
def test_dissociate_not_associated(trunk, custom):
    response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).delete()
    response.assert_deleted()


@fixtures.trunk(wazo_tenant=MAIN_TENANT)
@fixtures.trunk(wazo_tenant=SUB_TENANT)
@fixtures.custom(wazo_tenant=MAIN_TENANT)
@fixtures.custom(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(main_trunk, sub_trunk, main_custom, sub_custom):
    response = (
        confd.trunks(main_trunk['id'])
        .endpoints.custom(sub_custom['id'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Trunk'))

    response = (
        confd.trunks(sub_trunk['id'])
        .endpoints.custom(main_custom['id'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('CustomEndpoint'))


@fixtures.trunk()
@fixtures.custom()
def test_get_endpoint_custom_relation(trunk, custom):
    with a.trunk_endpoint_custom(trunk, custom):
        response = confd.trunks(trunk['id']).get()
        assert_that(
            response.item,
            has_entries(
                endpoint_custom=has_entries(
                    id=custom['id'], interface=custom['interface']
                )
            ),
        )


@fixtures.trunk()
@fixtures.custom()
def test_get_trunk_relation(trunk, custom):
    with a.trunk_endpoint_custom(trunk, custom):
        response = confd.endpoints.custom(custom['id']).get()
        assert_that(response.item, has_entries(trunk=has_entries(id=trunk['id'])))


@fixtures.trunk()
@fixtures.custom()
def test_delete_trunk_when_trunk_and_endpoint_associated(trunk, custom):
    with a.trunk_endpoint_custom(trunk, custom, check=False):
        confd.trunks(trunk['id']).delete().assert_deleted()

        deleted_trunk = confd.trunks(trunk['id']).get
        deleted_custom = confd.endpoints.custom(custom['id']).get
        s.check_resource_not_found(deleted_trunk, 'Trunk')
        s.check_resource_not_found(deleted_custom, 'CustomEndpoint')


@fixtures.trunk()
@fixtures.custom()
def test_delete_custom_when_trunk_and_custom_associated(trunk, custom):
    with a.trunk_endpoint_custom(trunk, custom, check=False):
        confd.endpoints.custom(custom['id']).delete().assert_deleted()

        response = confd.trunks(trunk['id']).get()
        assert_that(response.item, has_entries(endpoint_custom=None))


@fixtures.trunk()
@fixtures.custom()
def test_bus_events(trunk, custom):
    url = confd.trunks(trunk['id']).endpoints.custom(custom['id'])
    headers = {'tenant_uuid': trunk['tenant_uuid']}

    s.check_event('trunk_endpoint_custom_associated', headers, url.put)
    s.check_event('trunk_endpoint_custom_dissociated', headers, url.delete)
