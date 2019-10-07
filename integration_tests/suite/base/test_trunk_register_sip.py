# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries, none

from ..helpers import scenarios as s, errors as e, fixtures, associations as a
from . import confd

FAKE_ID = 999999999


@fixtures.trunk()
@fixtures.register_sip()
def test_associate_errors(trunk, register):
    fake_trunk = confd.trunks(FAKE_ID).registers.sip(register['id']).put
    fake_register = confd.trunks(trunk['id']).registers.sip(FAKE_ID).put

    yield s.check_resource_not_found, fake_trunk, 'Trunk'
    yield s.check_resource_not_found, fake_register, 'SIPRegister'


@fixtures.trunk()
@fixtures.register_sip()
def test_dissociate_errors(trunk, register):
    fake_trunk = confd.trunks(FAKE_ID).registers.sip(register['id']).delete
    fake_register = confd.trunks(trunk['id']).registers.sip(FAKE_ID).delete

    yield s.check_resource_not_found, fake_trunk, 'Trunk'
    yield s.check_resource_not_found, fake_register, 'SIPRegister'


@fixtures.trunk()
@fixtures.register_sip()
def test_associate(trunk, register):
    response = confd.trunks(trunk['id']).registers.sip(register['id']).put()
    response.assert_updated()


@fixtures.trunk()
@fixtures.register_sip()
def test_associate_already_associated(trunk, register):
    with a.trunk_register_sip(trunk, register):
        response = confd.trunks(trunk['id']).registers.sip(register['id']).put()
        response.assert_updated()


@fixtures.trunk()
@fixtures.register_sip()
@fixtures.register_sip()
def test_associate_multiple_register_sip_to_trunk(trunk, register1, register2):
    with a.trunk_register_sip(trunk, register1):
        response = confd.trunks(trunk['id']).registers.sip(register2['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'SIPRegister'))


@fixtures.trunk()
@fixtures.trunk()
@fixtures.register_sip()
def test_associate_multiple_trunks_to_register_sip(trunk1, trunk2, register):
    with a.trunk_register_sip(trunk1, register):
        response = confd.trunks(trunk2['id']).registers.sip(register['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'SIPRegister'))


@fixtures.trunk()
@fixtures.register_sip()
@fixtures.custom()
def test_associate_when_endpoint_custom(trunk, register, custom):
    with a.trunk_endpoint_custom(trunk, custom):
        response = confd.trunks(trunk['id']).registers.sip(register['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.register_sip()
@fixtures.iax()
def test_associate_when_endpoint_iax(trunk, register, iax):
    with a.trunk_endpoint_iax(trunk, iax):
        response = confd.trunks(trunk['id']).registers.sip(register['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.register_sip()
def test_dissociate(trunk, register):
    with a.trunk_register_sip(trunk, register, check=False):
        response = confd.trunks(trunk['id']).registers.sip(register['id']).delete()
        response.assert_deleted()


@fixtures.trunk()
@fixtures.register_sip()
def test_dissociate_not_associated(trunk, register):
    response = confd.trunks(trunk['id']).registers.sip(register['id']).delete()
    response.assert_deleted()


@fixtures.trunk()
@fixtures.register_sip()
def test_get_register_sip_relation(trunk, register):
    with a.trunk_register_sip(trunk, register):
        response = confd.trunks(trunk['id']).get()
        assert_that(
            response.item, has_entries(register_sip=has_entries(id=register['id']))
        )


@fixtures.trunk()
@fixtures.register_sip()
def test_get_trunk_relation(trunk, register):
    with a.trunk_register_sip(trunk, register):
        response = confd.registers.sip(register['id']).get()
        assert_that(response.item, has_entries(trunk=has_entries(id=trunk['id'])))


@fixtures.trunk()
@fixtures.register_sip()
def test_delete_trunk_when_trunk_and_register_associated(trunk, register):
    with a.trunk_register_sip(trunk, register, check=False):
        confd.trunks(trunk['id']).delete().assert_deleted()

        deleted_trunk = confd.trunks(trunk['id']).get
        deleted_register = confd.registers.sip(register['id']).get
        yield s.check_resource_not_found, deleted_trunk, 'Trunk'
        yield s.check_resource_not_found, deleted_register, 'SIPRegister'


@fixtures.trunk()
@fixtures.register_sip()
def test_delete_sip_when_trunk_and_sip_associated(trunk, register):
    with a.trunk_register_sip(trunk, register, check=False):
        confd.registers.sip(register['id']).delete().assert_deleted()

        response = confd.trunks(trunk['id']).get()
        assert_that(response.item, has_entries(register_sip=none()))


@fixtures.trunk()
@fixtures.register_sip()
def test_bus_events(trunk, register):
    url = confd.trunks(trunk['id']).registers.sip(register['id'])
    yield s.check_bus_event, 'config.trunks.registers.sip.updated', url.put
    yield s.check_bus_event, 'config.trunks.registers.sip.deleted', url.delete
