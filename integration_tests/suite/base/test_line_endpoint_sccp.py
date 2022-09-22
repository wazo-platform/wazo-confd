# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    has_entries,
    greater_than,
    none,
)

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import CONTEXT, MAIN_TENANT, SUB_TENANT


@fixtures.registrar()
def test_create_line_with_endpoint_sccp_with_all_parameters(registrar):
    response = confd.lines.post(
        context=CONTEXT,
        position=2,
        registrar=registrar['id'],
        provisioning_code='887865',
        endpoint_sccp={
            'options': [
                ["cid_name", "cid_name"],
                ["cid_num", "cid_num"],
                ["allow", "allow"],
                ["disallow", "disallow"],
            ],
        },
    )

    try:
        line_id = response.item['id']
        endpoint_sccp_id = response.item['endpoint_sccp']['id']
        assert_that(
            response.item,
            has_entries(
                context=CONTEXT,
                position=2,
                device_slot=2,
                name=none(),
                protocol=none(),
                device_id=none(),
                caller_id_name=none(),
                caller_id_num=none(),
                registrar=registrar['id'],
                provisioning_code="887865",
                provisioning_extension="887865",
                tenant_uuid=MAIN_TENANT,
                endpoint_sccp=has_entries(
                    id=greater_than(0),
                    options=contains_inanyorder(
                        ["cid_name", "cid_name"],
                        ["cid_num", "cid_num"],
                        ["allow", "allow"],
                        ["disallow", "disallow"],
                    ),
                ),
            ),
        )

        assert_that(
            confd.lines(line_id).get().item,
            has_entries(
                endpoint_sccp=has_entries(id=endpoint_sccp_id),
            ),
        )

    finally:
        confd.lines(response.item['id']).delete().assert_deleted()


@fixtures.line()
@fixtures.sccp()
def test_associate_errors(line, sccp):
    fake_line = confd.lines(999999999).endpoints.sccp(sccp['id']).put
    fake_sccp = confd.lines(line['id']).endpoints.sccp(999999999).put

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_sccp, 'SCCPEndpoint'


@fixtures.line()
@fixtures.sccp()
def test_dissociate_errors(line, sccp):
    fake_line = confd.lines(999999999).endpoints.sccp(sccp['id']).delete
    fake_sccp = confd.lines(line['id']).endpoints.sccp(999999999).delete

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_sccp, 'SCCPEndpoint'


@fixtures.line()
@fixtures.sccp()
def test_associate(line, sccp):
    response = confd.lines(line['id']).endpoints.sccp(sccp['id']).put()
    response.assert_updated()


@fixtures.line()
@fixtures.sccp()
def test_associate_when_endpoint_already_associated(line, sccp):
    with a.line_endpoint_sccp(line, sccp):
        response = confd.lines(line['id']).endpoints.sccp(sccp['id']).put()
        response.assert_updated()


@fixtures.line()
@fixtures.sccp()
@fixtures.sccp()
def test_associate_with_another_endpoint_when_already_associated(line, sccp1, sccp2):
    with a.line_endpoint_sccp(line, sccp1):
        response = confd.lines(line['id']).endpoints.sccp(sccp2['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.line()
@fixtures.line()
@fixtures.sccp()
def test_associate_multiple_lines_to_sccp(line1, line2, sccp):
    with a.line_endpoint_sccp(line1, sccp):
        response = confd.lines(line2['id']).endpoints.sccp(sccp['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.line(context='main-internal')
@fixtures.line(context='sub-internal')
@fixtures.sccp(wazo_tenant=MAIN_TENANT)
@fixtures.sccp(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(_, __, main_line, sub_line, main_sccp, sub_sccp):
    response = (
        confd.lines(main_line['id'])
        .endpoints.sccp(sub_sccp['id'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Line'))

    response = (
        confd.lines(sub_line['id'])
        .endpoints.sccp(main_sccp['id'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('SCCPEndpoint'))

    response = (
        confd.lines(main_line['id'])
        .endpoints.sccp(sub_sccp['id'])
        .put(wazo_tenant=MAIN_TENANT)
    )
    response.assert_match(400, e.different_tenant())


@fixtures.line()
@fixtures.sccp()
def test_dissociate(line, sccp):
    with a.line_endpoint_sccp(line, sccp, check=False):
        response = confd.lines(line['id']).endpoints.sccp(sccp['id']).delete()
        response.assert_deleted()


@fixtures.line()
@fixtures.sccp()
def test_dissociate_when_not_associated(line, sccp):
    response = confd.lines(line['id']).endpoints.sccp(sccp['id']).delete()
    response.assert_deleted()


@fixtures.line()
@fixtures.sccp()
@fixtures.user()
def test_dissociate_when_associated_to_user(line, sccp, user):
    with a.line_endpoint_sccp(line, sccp), a.user_line(user, line):
        response = confd.lines(line['id']).endpoints.sccp(sccp['id']).delete()
        response.assert_match(400, e.resource_associated('Line', 'User'))


@fixtures.line()
@fixtures.sccp()
@fixtures.extension()
def test_dissociate_when_associated_to_extension(line, sccp, extension):
    with a.line_endpoint_sccp(line, sccp), a.line_extension(line, extension):
        response = confd.lines(line['id']).endpoints.sccp(sccp['id']).delete()
        response.assert_match(400, e.resource_associated('Line', 'Extension'))


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.line(context='main-internal')
@fixtures.line(context='sub-internal')
@fixtures.sccp(wazo_tenant=MAIN_TENANT)
@fixtures.sccp(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(_, __, main_line, sub_line, main_sccp, sub_sccp):
    response = (
        confd.lines(main_line['id'])
        .endpoints.sccp(sub_sccp['id'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Line'))

    response = (
        confd.lines(sub_line['id'])
        .endpoints.sccp(main_sccp['id'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('SCCPEndpoint'))


@fixtures.line()
@fixtures.sccp()
def test_get_endpoint_sccp_relation(line, sccp):
    with a.line_endpoint_sccp(line, sccp):
        response = confd.lines(line['id']).get()
        assert_that(
            response.item, has_entries(endpoint_sccp=has_entries(id=sccp['id']))
        )


@fixtures.line()
@fixtures.sccp()
def test_get_line_relation(line, sccp):
    with a.line_endpoint_sccp(line, sccp):
        response = confd.endpoints.sccp(sccp['id']).get()
        assert_that(response.item, has_entries(line=has_entries(id=line['id'])))


@fixtures.line()
@fixtures.sccp()
def test_delete_endpoint_dissociates_line(line, sccp):
    with a.line_endpoint_sccp(line, sccp, check=False):
        response = confd.endpoints.sccp(sccp['id']).delete()
        response.assert_deleted()

        response = confd.lines(line['id']).get()
        assert_that(response.item, has_entries(endpoint_sccp=None))


@fixtures.line()
@fixtures.sccp()
def test_bus_events(line, sccp):
    url = confd.lines(line['id']).endpoints.sccp(sccp['id'])
    headers = {'tenant_uuid': MAIN_TENANT}

    yield s.check_event, 'line_endpoint_sccp_associated', headers, url.put
    yield s.check_event, 'line_endpoint_sccp_dissociated', headers, url.delete
