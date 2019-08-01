# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_entries,
)

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)

FAKE_ID = 999999999


def test_associate_errors():
    with fixtures.trunk() as trunk, fixtures.custom() as custom:
        fake_trunk = confd.trunks(FAKE_ID).endpoints.custom(custom['id']).put
        fake_custom = confd.trunks(trunk['id']).endpoints.custom(FAKE_ID).put

        s.check_resource_not_found(fake_trunk, 'Trunk')
        s.check_resource_not_found(fake_custom, 'CustomEndpoint')



def test_dissociate_errors():
    with fixtures.trunk() as trunk, fixtures.custom() as custom:
        fake_trunk = confd.trunks(FAKE_ID).endpoints.custom(custom['id']).delete
        fake_custom = confd.trunks(trunk['id']).endpoints.custom(FAKE_ID).delete

        s.check_resource_not_found(fake_trunk, 'Trunk')
        s.check_resource_not_found(fake_custom, 'CustomEndpoint')



def test_get_errors():
    fake_trunk = confd.trunks(FAKE_ID).endpoints.custom.get
    fake_custom = confd.endpoints.custom(FAKE_ID).trunks.get

    s.check_resource_not_found(fake_trunk, 'Trunk')
    s.check_resource_not_found(fake_custom, 'CustomEndpoint')


def test_associate():
    with fixtures.trunk() as trunk, fixtures.custom() as custom:
        response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).put()
        response.assert_updated()



def test_associate_already_associated():
    with fixtures.trunk() as trunk, fixtures.custom() as custom:
        with a.trunk_endpoint_custom(trunk, custom):
            response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).put()
            response.assert_updated()


def test_associate_multiple_custom_to_trunk():
    with fixtures.trunk() as trunk, fixtures.custom() as custom1, fixtures.custom() as custom2:
        with a.trunk_endpoint_custom(trunk, custom1):
            response = confd.trunks(trunk['id']).endpoints.custom(custom2['id']).put()
            response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


def test_associate_multiple_trunks_to_custom():
    with fixtures.trunk() as trunk1, fixtures.trunk() as trunk2, fixtures.custom() as custom:
        with a.trunk_endpoint_custom(trunk1, custom):
            response = confd.trunks(trunk2['id']).endpoints.custom(custom['id']).put()
            response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


def test_associate_when_line_already_associated():
    with fixtures.trunk() as trunk, fixtures.line() as line, fixtures.custom() as custom:
        with a.line_endpoint_custom(line, custom):
            response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).put()
            response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


def test_associate_when_register_iax():
    with fixtures.trunk() as trunk, fixtures.custom() as custom, fixtures.register_iax() as register:
        with a.trunk_register_iax(trunk, register):
            response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).put()
            response.assert_match(400, e.resource_associated('Trunk', 'IAXRegister'))


def test_associate_when_register_sip():
    with fixtures.trunk() as trunk, fixtures.custom() as custom, fixtures.register_sip() as register:
        with a.trunk_register_sip(trunk, register):
            response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).put()
            response.assert_match(400, e.resource_associated('Trunk', 'SIPRegister'))


def test_associate_multi_tenant():
    with fixtures.trunk(wazo_tenant=MAIN_TENANT) as main_trunk, fixtures.trunk(wazo_tenant=SUB_TENANT) as sub_trunk, fixtures.custom(wazo_tenant=MAIN_TENANT) as main_custom, fixtures.custom(wazo_tenant=SUB_TENANT) as sub_custom:
        response = confd.trunks(main_trunk['id']).endpoints.custom(sub_custom['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Trunk'))

        response = confd.trunks(sub_trunk['id']).endpoints.custom(main_custom['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('CustomEndpoint'))

        response = confd.trunks(main_trunk['id']).endpoints.custom(sub_custom['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_get_endpoint_associated_to_trunk():
    with fixtures.trunk() as trunk, fixtures.custom() as custom:
        with a.trunk_endpoint_custom(trunk, custom):
            response = confd.trunks(trunk['id']).endpoints.custom.get()
            assert_that(
                response.item,
                has_entries(
                    trunk_id=trunk['id'],
                    endpoint='custom',
                    endpoint_id=custom['id'],
                )
            )


def test_get_trunk_associated_to_endpoint():
    with fixtures.trunk() as trunk, fixtures.custom() as custom:
        with a.trunk_endpoint_custom(trunk, custom):
            response = confd.endpoints.custom(custom['id']).trunks.get()
            assert_that(
                response.item,
                has_entries(
                    trunk_id=trunk['id'],
                    endpoint='custom',
                    endpoint_id=custom['id'],
                )
            )


def test_get_no_endpoint():
    with fixtures.trunk() as trunk:
        response = confd.trunks(trunk['id']).endpoints.custom.get()
        response.assert_match(404, e.not_found('TrunkEndpoint'))



def test_dissociate():
    with fixtures.trunk() as trunk, fixtures.custom() as custom:
        with a.trunk_endpoint_custom(trunk, custom, check=False):
            response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.trunk() as trunk, fixtures.custom() as custom:
        response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.trunk(wazo_tenant=MAIN_TENANT) as main_trunk, fixtures.trunk(wazo_tenant=SUB_TENANT) as sub_trunk, fixtures.custom(wazo_tenant=MAIN_TENANT) as main_custom, fixtures.custom(wazo_tenant=SUB_TENANT) as sub_custom:
        response = confd.trunks(main_trunk['id']).endpoints.custom(sub_custom['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Trunk'))

        response = confd.trunks(sub_trunk['id']).endpoints.custom(main_custom['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('CustomEndpoint'))



def test_get_endpoint_custom_relation():
    with fixtures.trunk() as trunk, fixtures.custom() as custom:
        with a.trunk_endpoint_custom(trunk, custom):
            response = confd.trunks(trunk['id']).get()
            assert_that(
                response.item,
                has_entries(
                    endpoint_custom=has_entries(
                        id=custom['id'],
                        interface=custom['interface']
                    )
                )
            )


def test_get_trunk_relation():
    with fixtures.trunk() as trunk, fixtures.custom() as custom:
        with a.trunk_endpoint_custom(trunk, custom):
            response = confd.endpoints.custom(custom['id']).get()
            assert_that(
                response.item,
                has_entries(
                    trunk=has_entries(id=trunk['id'])
                )
            )


def test_delete_trunk_when_trunk_and_endpoint_associated():
    with fixtures.trunk() as trunk, fixtures.custom() as custom:
        with a.trunk_endpoint_custom(trunk, custom, check=False):
            confd.trunks(trunk['id']).delete().assert_deleted()

            deleted_trunk = confd.trunks(custom['id']).endpoints.custom.get
            deleted_custom = confd.endpoints.custom(custom['id']).trunks.get
            s.check_resource_not_found(deleted_trunk, 'Trunk')
            s.check_resource_not_found(deleted_custom, 'CustomEndpoint')


def test_delete_custom_when_trunk_and_custom_associated():
    with fixtures.trunk() as trunk, fixtures.custom() as custom:
        with a.trunk_endpoint_custom(trunk, custom, check=False):
            confd.endpoints.custom(custom['id']).delete().assert_deleted()

            response = confd.trunks(trunk['id']).endpoints.custom.get()
            response.assert_match(404, e.not_found('TrunkEndpoint'))


def test_bus_events():
    with fixtures.trunk() as trunk, fixtures.custom() as custom:
        url = confd.trunks(trunk['id']).endpoints.custom(custom['id'])
        s.check_bus_event('config.trunks.endpoints.updated', url.put)
        s.check_bus_event('config.trunks.endpoints.deleted', url.delete)

