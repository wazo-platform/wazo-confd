# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
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


@fixtures.trunk()
@fixtures.register_iax()
def test_associate_errors(trunk, register):
    fake_trunk = confd.trunks(FAKE_ID).registers.iax(register['id']).put
    fake_register = confd.trunks(trunk['id']).registers.iax(FAKE_ID).put

    yield s.check_resource_not_found, fake_trunk, 'Trunk'
    yield s.check_resource_not_found, fake_register, 'IAXRegister'


@fixtures.trunk()
@fixtures.register_iax()
def test_dissociate_errors(trunk, register):
    fake_trunk = confd.trunks(FAKE_ID).registers.iax(register['id']).delete
    fake_register = confd.trunks(trunk['id']).registers.iax(FAKE_ID).delete

    yield s.check_resource_not_found, fake_trunk, 'Trunk'
    yield s.check_resource_not_found, fake_register, 'IAXRegister'


@fixtures.trunk()
@fixtures.register_iax()
def test_associate(trunk, register):
    response = confd.trunks(trunk['id']).registers.iax(register['id']).put()
    response.assert_updated()


@fixtures.trunk()
@fixtures.register_iax()
def test_associate_already_associated(trunk, register):
    with a.trunk_register_iax(trunk, register):
        response = confd.trunks(trunk['id']).registers.iax(register['id']).put()
        response.assert_updated()


@fixtures.trunk()
@fixtures.register_iax()
@fixtures.register_iax()
def test_associate_multiple_register_iax_to_trunk(trunk, register1, register2):
    with a.trunk_register_iax(trunk, register1):
        response = confd.trunks(trunk['id']).registers.iax(register2['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'IAXRegister'))


@fixtures.trunk()
@fixtures.trunk()
@fixtures.register_iax()
def test_associate_multiple_trunks_to_register_iax(trunk1, trunk2, register):
    with a.trunk_register_iax(trunk1, register):
        response = confd.trunks(trunk2['id']).registers.iax(register['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'IAXRegister'))


@fixtures.trunk()
@fixtures.register_iax()
@fixtures.custom()
def test_associate_when_endpoint_custom(trunk, register, custom):
    with a.trunk_endpoint_custom(trunk, custom):
        response = confd.trunks(trunk['id']).registers.iax(register['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.register_iax()
@fixtures.sip()
def test_associate_when_endpoint_sip(trunk, register, sip):
    with a.trunk_endpoint_sip(trunk, sip):
        response = confd.trunks(trunk['id']).registers.iax(register['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.register_iax()
def test_dissociate(trunk, register):
    with a.trunk_register_iax(trunk, register, check=False):
        response = confd.trunks(trunk['id']).registers.iax(register['id']).delete()
        response.assert_deleted()


@fixtures.trunk()
@fixtures.register_iax()
def test_dissociate_not_associated(trunk, register):
    response = confd.trunks(trunk['id']).registers.iax(register['id']).delete()
    response.assert_deleted()


@fixtures.trunk()
@fixtures.register_iax()
def test_get_register_iax_relation(trunk, register):
    with a.trunk_register_iax(trunk, register):
        response = confd.trunks(trunk['id']).get()
        assert_that(response.item, has_entries(
            register_iax=has_entries(id=register['id'])
        ))


@fixtures.trunk()
@fixtures.register_iax()
def test_get_trunk_relation(trunk, register):
    with a.trunk_register_iax(trunk, register):
        response = confd.registers.iax(register['id']).get()
        assert_that(response.item, has_entries(
            trunk=has_entries(id=trunk['id'])
        ))


@fixtures.trunk()
@fixtures.register_iax()
def test_delete_trunk_when_trunk_and_register_associated(trunk, register):
    with a.trunk_register_iax(trunk, register, check=False):
        confd.trunks(trunk['id']).delete().assert_deleted()

        deleted_trunk = confd.trunks(trunk['id']).get
        deleted_register = confd.registers.iax(register['id']).get
        yield s.check_resource_not_found, deleted_trunk, 'Trunk'
        yield s.check_resource_not_found, deleted_register, 'IAXRegister'


@fixtures.trunk()
@fixtures.register_iax()
def test_delete_iax_when_trunk_and_iax_associated(trunk, register):
    with a.trunk_register_iax(trunk, register, check=False):
        confd.registers.iax(register['id']).delete().assert_deleted()

        response = confd.trunks(trunk['id']).get()
        assert_that(response.item, has_entries(
            register_iax=none()
        ))


@fixtures.trunk()
@fixtures.register_iax()
def test_bus_events(trunk, register):
    url = confd.trunks(trunk['id']).registers.iax(register['id'])
    yield s.check_bus_event, 'config.trunks.registers.iax.updated', url.put
    yield s.check_bus_event, 'config.trunks.registers.iax.deleted', url.delete
