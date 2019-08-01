# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_entries,
    none,
)

from ..helpers import (
    scenarios as s,
    errors as e,
    fixtures,
    associations as a,
)
from . import confd

FAKE_ID = 999999999


def test_associate_errors():
    with fixtures.trunk() as trunk, fixtures.register_iax() as register:
        fake_trunk = confd.trunks(FAKE_ID).registers.iax(register['id']).put
        fake_register = confd.trunks(trunk['id']).registers.iax(FAKE_ID).put

        s.check_resource_not_found(fake_trunk, 'Trunk')
        s.check_resource_not_found(fake_register, 'IAXRegister')



def test_dissociate_errors():
    with fixtures.trunk() as trunk, fixtures.register_iax() as register:
        fake_trunk = confd.trunks(FAKE_ID).registers.iax(register['id']).delete
        fake_register = confd.trunks(trunk['id']).registers.iax(FAKE_ID).delete

        s.check_resource_not_found(fake_trunk, 'Trunk')
        s.check_resource_not_found(fake_register, 'IAXRegister')



def test_associate():
    with fixtures.trunk() as trunk, fixtures.register_iax() as register:
        response = confd.trunks(trunk['id']).registers.iax(register['id']).put()
        response.assert_updated()



def test_associate_already_associated():
    with fixtures.trunk() as trunk, fixtures.register_iax() as register:
        with a.trunk_register_iax(trunk, register):
            response = confd.trunks(trunk['id']).registers.iax(register['id']).put()
            response.assert_updated()


def test_associate_multiple_register_iax_to_trunk():
    with fixtures.trunk() as trunk, fixtures.register_iax() as register1, fixtures.register_iax() as register2:
        with a.trunk_register_iax(trunk, register1):
            response = confd.trunks(trunk['id']).registers.iax(register2['id']).put()
            response.assert_match(400, e.resource_associated('Trunk', 'IAXRegister'))


def test_associate_multiple_trunks_to_register_iax():
    with fixtures.trunk() as trunk1, fixtures.trunk() as trunk2, fixtures.register_iax() as register:
        with a.trunk_register_iax(trunk1, register):
            response = confd.trunks(trunk2['id']).registers.iax(register['id']).put()
            response.assert_match(400, e.resource_associated('Trunk', 'IAXRegister'))


def test_associate_when_endpoint_custom():
    with fixtures.trunk() as trunk, fixtures.register_iax() as register, fixtures.custom() as custom:
        with a.trunk_endpoint_custom(trunk, custom):
            response = confd.trunks(trunk['id']).registers.iax(register['id']).put()
            response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


def test_associate_when_endpoint_sip():
    with fixtures.trunk() as trunk, fixtures.register_iax() as register, fixtures.sip() as sip:
        with a.trunk_endpoint_sip(trunk, sip):
            response = confd.trunks(trunk['id']).registers.iax(register['id']).put()
            response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


def test_dissociate():
    with fixtures.trunk() as trunk, fixtures.register_iax() as register:
        with a.trunk_register_iax(trunk, register, check=False):
            response = confd.trunks(trunk['id']).registers.iax(register['id']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.trunk() as trunk, fixtures.register_iax() as register:
        response = confd.trunks(trunk['id']).registers.iax(register['id']).delete()
        response.assert_deleted()



def test_get_register_iax_relation():
    with fixtures.trunk() as trunk, fixtures.register_iax() as register:
        with a.trunk_register_iax(trunk, register):
            response = confd.trunks(trunk['id']).get()
            assert_that(response.item, has_entries(
                register_iax=has_entries(id=register['id'])
            ))


def test_get_trunk_relation():
    with fixtures.trunk() as trunk, fixtures.register_iax() as register:
        with a.trunk_register_iax(trunk, register):
            response = confd.registers.iax(register['id']).get()
            assert_that(response.item, has_entries(
                trunk=has_entries(id=trunk['id'])
            ))


def test_delete_trunk_when_trunk_and_register_associated():
    with fixtures.trunk() as trunk, fixtures.register_iax() as register:
        with a.trunk_register_iax(trunk, register, check=False):
            confd.trunks(trunk['id']).delete().assert_deleted()

            deleted_trunk = confd.trunks(trunk['id']).get
            deleted_register = confd.registers.iax(register['id']).get
            s.check_resource_not_found(deleted_trunk, 'Trunk')
            s.check_resource_not_found(deleted_register, 'IAXRegister')


def test_delete_iax_when_trunk_and_iax_associated():
    with fixtures.trunk() as trunk, fixtures.register_iax() as register:
        with a.trunk_register_iax(trunk, register, check=False):
            confd.registers.iax(register['id']).delete().assert_deleted()

            response = confd.trunks(trunk['id']).get()
            assert_that(response.item, has_entries(
                register_iax=none()
            ))


def test_bus_events():
    with fixtures.trunk() as trunk, fixtures.register_iax() as register:
        url = confd.trunks(trunk['id']).registers.iax(register['id'])
        s.check_bus_event('config.trunks.registers.iax.updated', url.put)
        s.check_bus_event('config.trunks.registers.iax.deleted', url.delete)

