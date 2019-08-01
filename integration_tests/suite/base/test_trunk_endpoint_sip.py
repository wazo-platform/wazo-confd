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
    with fixtures.trunk() as trunk, fixtures.sip() as sip:
        fake_trunk = confd.trunks(FAKE_ID).endpoints.sip(sip['id']).put
        fake_sip = confd.trunks(trunk['id']).endpoints.sip(FAKE_ID).put

        s.check_resource_not_found(fake_trunk, 'Trunk')
        s.check_resource_not_found(fake_sip, 'SIPEndpoint')



def test_dissociate_errors():
    with fixtures.trunk() as trunk, fixtures.sip() as sip:
        fake_trunk = confd.trunks(FAKE_ID).endpoints.sip(sip['id']).delete
        fake_sip = confd.trunks(trunk['id']).endpoints.sip(FAKE_ID).delete

        s.check_resource_not_found(fake_trunk, 'Trunk')
        s.check_resource_not_found(fake_sip, 'SIPEndpoint')



def test_get_errors():
    fake_trunk = confd.trunks(FAKE_ID).endpoints.sip.get
    fake_sip = confd.endpoints.sip(FAKE_ID).trunks.get

    s.check_resource_not_found(fake_trunk, 'Trunk')
    s.check_resource_not_found(fake_sip, 'SIPEndpoint')


def test_associate():
    with fixtures.trunk() as trunk, fixtures.sip() as sip:
        response = confd.trunks(trunk['id']).endpoints.sip(sip['id']).put()
        response.assert_updated()



def test_associate_already_associated():
    with fixtures.trunk() as trunk, fixtures.sip() as sip:
        with a.trunk_endpoint_sip(trunk, sip):
            response = confd.trunks(trunk['id']).endpoints.sip(sip['id']).put()
            response.assert_updated()


def test_associate_multiple_sip_to_trunk():
    with fixtures.trunk() as trunk, fixtures.sip() as sip1, fixtures.sip() as sip2:
        with a.trunk_endpoint_sip(trunk, sip1):
            response = confd.trunks(trunk['id']).endpoints.sip(sip2['id']).put()
            response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


def test_associate_multiple_trunks_to_sip():
    with fixtures.trunk() as trunk1, fixtures.trunk() as trunk2, fixtures.sip() as sip:
        with a.trunk_endpoint_sip(trunk1, sip):
            response = confd.trunks(trunk2['id']).endpoints.sip(sip['id']).put()
            response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


def test_associate_when_line_already_associated():
    with fixtures.trunk() as trunk, fixtures.line() as line, fixtures.sip() as sip:
        with a.line_endpoint_sip(line, sip):
            response = confd.trunks(trunk['id']).endpoints.sip(sip['id']).put()
            response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


def test_associate_when_register_iax():
    with fixtures.trunk() as trunk, fixtures.sip() as sip, fixtures.register_iax() as register:
        with a.trunk_register_iax(trunk, register):
            response = confd.trunks(trunk['id']).endpoints.sip(sip['id']).put()
            response.assert_match(400, e.resource_associated('Trunk', 'IAXRegister'))


def test_associate_multi_tenant():
    with fixtures.trunk(wazo_tenant=MAIN_TENANT) as main_trunk, fixtures.trunk(wazo_tenant=SUB_TENANT) as sub_trunk, fixtures.sip(wazo_tenant=MAIN_TENANT) as main_sip, fixtures.sip(wazo_tenant=SUB_TENANT) as sub_sip:
        response = confd.trunks(main_trunk['id']).endpoints.sip(sub_sip['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Trunk'))

        response = confd.trunks(sub_trunk['id']).endpoints.sip(main_sip['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('SIPEndpoint'))

        response = confd.trunks(main_trunk['id']).endpoints.sip(sub_sip['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_get_endpoint_associated_to_trunk():
    with fixtures.trunk() as trunk, fixtures.sip() as sip:
        with a.trunk_endpoint_sip(trunk, sip):
            response = confd.trunks(trunk['id']).endpoints.sip.get()
            assert_that(
                response.item,
                has_entries(
                    trunk_id=trunk['id'],
                    endpoint='sip',
                    endpoint_id=sip['id'],
                )
            )


def test_get_trunk_associated_to_endpoint():
    with fixtures.trunk() as trunk, fixtures.sip() as sip:
        with a.trunk_endpoint_sip(trunk, sip):
            response = confd.endpoints.sip(sip['id']).trunks.get()
            assert_that(
                response.item,
                has_entries(
                    trunk_id=trunk['id'],
                    endpoint='sip',
                    endpoint_id=sip['id'],
                )
            )


def test_get_no_endpoint():
    with fixtures.trunk() as trunk:
        response = confd.trunks(trunk['id']).endpoints.sip.get()
        response.assert_match(404, e.not_found('TrunkEndpoint'))



def test_dissociate():
    with fixtures.trunk() as trunk, fixtures.sip() as sip:
        with a.trunk_endpoint_sip(trunk, sip, check=False):
            response = confd.trunks(trunk['id']).endpoints.sip(sip['id']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.trunk() as trunk, fixtures.sip() as sip:
        response = confd.trunks(trunk['id']).endpoints.sip(sip['id']).delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.trunk(wazo_tenant=MAIN_TENANT) as main_trunk, fixtures.trunk(wazo_tenant=SUB_TENANT) as sub_trunk, fixtures.sip(wazo_tenant=MAIN_TENANT) as main_sip, fixtures.sip(wazo_tenant=SUB_TENANT) as sub_sip:
        response = confd.trunks(main_trunk['id']).endpoints.sip(sub_sip['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Trunk'))

        response = confd.trunks(sub_trunk['id']).endpoints.sip(main_sip['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('SIPEndpoint'))



def test_get_endpoint_sip_relation():
    with fixtures.trunk() as trunk, fixtures.sip() as sip:
        with a.trunk_endpoint_sip(trunk, sip):
            response = confd.trunks(trunk['id']).get()
            assert_that(
                response.item,
                has_entries(
                    endpoint_sip=has_entries(id=sip['id'], username=sip['username'])
                )
            )


def test_get_trunk_relation():
    with fixtures.trunk() as trunk, fixtures.sip() as sip:
        with a.trunk_endpoint_sip(trunk, sip):
            response = confd.endpoints.sip(sip['id']).get()
            assert_that(
                response.item,
                has_entries(trunk=has_entries(id=trunk['id']))
            )


def test_delete_trunk_when_trunk_and_endpoint_associated():
    with fixtures.trunk() as trunk, fixtures.sip() as sip:
        with a.trunk_endpoint_sip(trunk, sip, check=False):
            confd.trunks(trunk['id']).delete().assert_deleted()

            deleted_trunk = confd.trunks(trunk['id']).endpoints.sip.get
            deleted_sip = confd.endpoints.sip(sip['id']).trunks.get
            s.check_resource_not_found(deleted_trunk, 'Trunk')
            s.check_resource_not_found(deleted_sip, 'SIPEndpoint')


def test_delete_sip_when_trunk_and_sip_associated():
    with fixtures.trunk() as trunk, fixtures.sip() as sip:
        with a.trunk_endpoint_sip(trunk, sip, check=False):
            confd.endpoints.sip(sip['id']).delete().assert_deleted()

            response = confd.trunks(trunk['id']).endpoints.sip.get()
            response.assert_match(404, e.not_found('TrunkEndpoint'))


def test_bus_events():
    with fixtures.trunk() as trunk, fixtures.sip() as sip:
        url = confd.trunks(trunk['id']).endpoints.sip(sip['id'])
        s.check_bus_event('config.trunks.endpoints.updated', url.put)
        s.check_bus_event('config.trunks.endpoints.deleted', url.delete)

