# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries, none

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT, SUB_TENANT2
from . import confd

FAKE_ID = 999999999


@fixtures.trunk()
@fixtures.register_iax()
def test_associate_errors(trunk, register):
    fake_trunk = confd.trunks(FAKE_ID).registers.iax(register['id']).put
    fake_register = confd.trunks(trunk['id']).registers.iax(FAKE_ID).put

    s.check_resource_not_found(fake_trunk, 'Trunk')
    s.check_resource_not_found(fake_register, 'IAXRegister')


@fixtures.trunk()
@fixtures.register_iax()
def test_dissociate_errors(trunk, register):
    fake_trunk = confd.trunks(FAKE_ID).registers.iax(register['id']).delete
    fake_register = confd.trunks(trunk['id']).registers.iax(FAKE_ID).delete

    s.check_resource_not_found(fake_trunk, 'Trunk')
    s.check_resource_not_found(fake_register, 'IAXRegister')


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
        assert_that(
            response.item, has_entries(register_iax=has_entries(id=register['id']))
        )


@fixtures.trunk()
@fixtures.register_iax()
def test_get_trunk_relation(trunk, register):
    with a.trunk_register_iax(trunk, register):
        response = confd.registers.iax(register['id']).get()
        assert_that(response.item, has_entries(trunk=has_entries(id=trunk['id'])))


@fixtures.trunk()
@fixtures.register_iax()
def test_delete_trunk_when_trunk_and_register_associated(trunk, register):
    with a.trunk_register_iax(trunk, register, check=False):
        confd.trunks(trunk['id']).delete().assert_deleted()

        deleted_trunk = confd.trunks(trunk['id']).get
        deleted_register = confd.registers.iax(register['id']).get
        s.check_resource_not_found(deleted_trunk, 'Trunk')
        s.check_resource_not_found(deleted_register, 'IAXRegister')


@fixtures.trunk()
@fixtures.register_iax()
def test_delete_iax_when_trunk_and_iax_associated(trunk, register):
    with a.trunk_register_iax(trunk, register, check=False):
        confd.registers.iax(register['id']).delete().assert_deleted()

        response = confd.trunks(trunk['id']).get()
        assert_that(response.item, has_entries(register_iax=none()))


@fixtures.trunk()
@fixtures.register_iax()
def test_bus_events(trunk, register):
    url = confd.trunks(trunk['id']).registers.iax(register['id'])
    headers = {'tenant_uuid': trunk['tenant_uuid']}

    s.check_event('trunk_register_iax_associated', headers, url.put)
    s.check_event('trunk_register_iax_dissociated', headers, url.delete)


def put_register(trunk, register):
    def call(**kwargs):
        url = confd.trunks(trunk['id']).registers.iax(register['id'])
        return url.put(**kwargs)

    return call


def delete_register(trunk, register):
    def call(**kwargs):
        url = confd.trunks(trunk['id']).registers.iax(register['id'])
        return url.delete(**kwargs)

    return call


@fixtures.trunk(wazo_tenant=MAIN_TENANT)
@fixtures.trunk(wazo_tenant=SUB_TENANT2)
@fixtures.register_iax()
@fixtures.register_iax()
def test_register_trunk_outside_tenant(main_trunk, sibling_trunk, register, register2):
    for trunk in (main_trunk, sibling_trunk):
        s.check_outside_tenant_not_found(
            put_register(trunk, register), 'Trunk', SUB_TENANT
        )

    with a.trunk_register_iax(main_trunk, register):
        put_register(sibling_trunk, register2)(wazo_tenant=SUB_TENANT2).assert_updated()
        for trunk, associated in ((main_trunk, register), (sibling_trunk, register2)):
            call = delete_register(trunk, associated)
            s.check_outside_tenant_not_found(call, 'Trunk', SUB_TENANT)
        delete_register(sibling_trunk, register2)(
            wazo_tenant=SUB_TENANT2
        ).assert_deleted()


@fixtures.trunk(wazo_tenant=SUB_TENANT)
@fixtures.register_iax()
def test_register_sub_tenant_trunk_from_main_tenant(sub_trunk, register):
    call = put_register(sub_trunk, register)
    s.check_sub_tenant_found(call, MAIN_TENANT, 204)
    response = confd.trunks(sub_trunk['id']).get()
    assert_that(response.item['register_iax'], has_entries(id=register['id']))

    call = delete_register(sub_trunk, register)
    s.check_sub_tenant_found(call, MAIN_TENANT, 204)
    response = confd.trunks(sub_trunk['id']).get()
    assert_that(response.item['register_iax'], none())


@fixtures.trunk(wazo_tenant=SUB_TENANT2)
@fixtures.register_iax()
def test_register_wazo_tenant_not_visible(sibling_trunk, register):
    for request in (put_register, delete_register):
        s.check_wazo_tenant_not_visible_refused(request(sibling_trunk, register))
