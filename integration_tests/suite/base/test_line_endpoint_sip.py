# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains, contains_inanyorder, has_entries

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import MAIN_TENANT, SUB_TENANT

FAKE_UUID = '99999999-9999-4999-9999-999999999999'
FAKE_ID = 999999999


@fixtures.line()
@fixtures.sip()
def test_associate_errors(line, sip):
    fake_line = confd.lines(FAKE_ID).endpoints.sip(sip['uuid']).put
    fake_sip = confd.lines(line['id']).endpoints.sip(FAKE_UUID).put

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_sip, 'SIPEndpoint'


@fixtures.line()
@fixtures.sip()
def test_dissociate_errors(line, sip):
    fake_line = confd.lines(FAKE_ID).endpoints.sip(sip['uuid']).delete
    fake_sip = confd.lines(line['id']).endpoints.sip(FAKE_UUID).delete

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_sip, 'SIPEndpoint'


@fixtures.line()
@fixtures.sip()
def test_associate(line, sip):
    response = confd.lines(line['id']).endpoints.sip(sip['uuid']).put()
    response.assert_updated()


@fixtures.line()
@fixtures.sip()
def test_associate_when_endpoint_already_associated(line, sip):
    with a.line_endpoint_sip(line, sip):
        response = confd.lines(line['id']).endpoints.sip(sip['uuid']).put()
        response.assert_updated()


@fixtures.line()
@fixtures.sip()
@fixtures.sip()
def test_associate_with_another_endpoint_when_already_associated(line, sip1, sip2):
    with a.line_endpoint_sip(line, sip1):
        response = confd.lines(line['id']).endpoints.sip(sip2['uuid']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.line()
@fixtures.line()
@fixtures.sip()
def test_associate_multiple_lines_to_sip(line1, line2, sip):
    with a.line_endpoint_sip(line1, sip):
        response = confd.lines(line2['id']).endpoints.sip(sip['uuid']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.line()
@fixtures.trunk()
@fixtures.sip()
def test_associate_when_trunk_already_associated(line, trunk, sip):
    with a.trunk_endpoint_sip(trunk, sip):
        response = confd.lines(line['id']).endpoints.sip(sip['uuid']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.line(context='main-internal')
@fixtures.line(context='sub-internal')
@fixtures.sip(wazo_tenant=MAIN_TENANT)
@fixtures.sip(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(_, __, main_line, sub_line, main_sip, sub_sip):
    response = (
        confd.lines(main_line['id'])
        .endpoints.sip(sub_sip['uuid'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Line'))

    response = (
        confd.lines(sub_line['id'])
        .endpoints.sip(main_sip['uuid'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('SIPEndpoint'))

    response = (
        confd.lines(main_line['id'])
        .endpoints.sip(sub_sip['uuid'])
        .put(wazo_tenant=MAIN_TENANT)
    )
    response.assert_match(400, e.different_tenant())


@fixtures.line()
@fixtures.sip()
def test_dissociate(line, sip):
    with a.line_endpoint_sip(line, sip, check=False):
        response = confd.lines(line['id']).endpoints.sip(sip['uuid']).delete()
        response.assert_deleted()


@fixtures.line()
@fixtures.sip()
def test_dissociate_when_not_associated(line, sip):
    response = confd.lines(line['id']).endpoints.sip(sip['uuid']).delete()
    response.assert_deleted()


@fixtures.line()
@fixtures.sip()
@fixtures.user()
def test_dissociate_when_associated_to_user(line, sip, user):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line):
        response = confd.lines(line['id']).endpoints.sip(sip['uuid']).delete()
        response.assert_match(400, e.resource_associated('Line', 'User'))


@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_dissociate_when_associated_to_extension(line, sip, extension):
    with a.line_endpoint_sip(line, sip), a.line_extension(line, extension):
        response = confd.lines(line['id']).endpoints.sip(sip['uuid']).delete()
        response.assert_match(400, e.resource_associated('Line', 'Extension'))


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.line(context='main-internal')
@fixtures.line(context='sub-internal')
@fixtures.sip(wazo_tenant=MAIN_TENANT)
@fixtures.sip(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(_, __, main_line, sub_line, main_sip, sub_sip):
    response = (
        confd.lines(main_line['id'])
        .endpoints.sip(sub_sip['uuid'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Line'))

    response = (
        confd.lines(sub_line['id'])
        .endpoints.sip(main_sip['uuid'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('SIPEndpoint'))


@fixtures.line()
@fixtures.sip(
    display_name='my-endpoint',
    auth_section_options=[['username', 'my-username'], ['password', 'my-password']],
)
def test_get_endpoint_sip_relation(line, sip):
    with a.line_endpoint_sip(line, sip):
        response = confd.lines(line['id']).get()
        assert_that(
            response.item,
            has_entries(
                endpoint_sip=has_entries(
                    uuid=sip['uuid'],
                    display_name=sip['display_name'],
                    auth_section_options=contains_inanyorder(
                        contains('username', 'my-username'),
                        contains('password', 'my-password'),
                    ),
                )
            ),
        )


@fixtures.line()
@fixtures.sip()
def test_get_line_relation(line, sip):
    with a.line_endpoint_sip(line, sip):
        response = confd.endpoints.sip(sip['uuid']).get()
        assert_that(response.item, has_entries(line=has_entries(id=line['id'])))


@fixtures.line()
@fixtures.sip()
def test_delete_endpoint_dissociates_line(line, sip):
    with a.line_endpoint_sip(line, sip, check=False):
        response = confd.endpoints.sip(sip['uuid']).delete()
        response.assert_deleted()

        response = confd.lines(line['id']).get()
        assert_that(response.item, has_entries(endpoint_sip=None))


@fixtures.line()
@fixtures.sip()
def test_bus_events(line, sip):
    url = confd.lines(line['id']).endpoints.sip(sip['uuid'])
    routing_key = 'config.lines.{}.endpoints.sip.{}.updated'.format(
        line['id'], sip['uuid']
    )
    yield s.check_bus_event, routing_key, url.put
    routing_key = 'config.lines.{}.endpoints.sip.{}.deleted'.format(
        line['id'], sip['uuid']
    )
    yield s.check_bus_event, routing_key, url.delete
