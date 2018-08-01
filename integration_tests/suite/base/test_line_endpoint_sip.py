# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    has_entries,
)

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    helpers as h,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)


@fixtures.line()
@fixtures.sip()
def test_associate_errors(line, sip):
    fake_line = confd.lines(999999999).endpoints.sip(sip['id']).put
    fake_sip = confd.lines(line['id']).endpoints.sip(999999999).put

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_sip, 'SIPEndpoint'


@fixtures.line()
@fixtures.sip()
def test_dissociate_errors(line, sip):
    fake_line = confd.lines(999999999).endpoints.sip(sip['id']).delete
    fake_sip = confd.lines(line['id']).endpoints.sip(999999999).delete

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_sip, 'SIPEndpoint'


def test_get_errors():
    fake_line = confd.lines(999999999).endpoints.sip.get
    fake_sip = confd.endpoints.sip(999999999).lines.get

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_sip, 'SIPEndpoint'


@fixtures.line()
@fixtures.sip()
def test_get_sip_endpoint_associated_to_line(line, sip):
    response = confd.lines(line['id']).endpoints.sip.get()
    response.assert_status(404)

    with a.line_endpoint_sip(line, sip):
        response = confd.lines(line['id']).endpoints.sip.get()
        assert_that(response.item, has_entries({'line_id': line['id'],
                                                'endpoint': 'sip',
                                                'endpoint_id': sip['id']}))


@fixtures.line()
@fixtures.sip()
def test_get_sip_endpoint_after_dissociation(line, sip):
    h.line_endpoint_sip.associate(line['id'], sip['id'])
    h.line_endpoint_sip.dissociate(line['id'], sip['id'])

    response = confd.lines(line['id']).endpoints.sip.get()
    response.assert_status(404)


@fixtures.line()
@fixtures.sip()
def test_get_line_associated_to_a_sip_endpoint(line, sip):
    response = confd.endpoints.sip(sip['id']).lines.get()
    response.assert_status(404)

    with a.line_endpoint_sip(line, sip):
        response = confd.endpoints.sip(sip['id']).lines.get()
        assert_that(response.item, has_entries({'line_id': line['id'],
                                                'endpoint': 'sip',
                                                'endpoint_id': sip['id']}))


@fixtures.line()
@fixtures.sip()
def test_associate(line, sip):
    response = confd.lines(line['id']).endpoints.sip(sip['id']).put()
    response.assert_updated()


@fixtures.line()
@fixtures.sip()
def test_associate_when_endpoint_already_associated(line, sip):
    with a.line_endpoint_sip(line, sip):
        response = confd.lines(line['id']).endpoints.sip(sip['id']).put()
        response.assert_updated()


@fixtures.line()
@fixtures.sip()
@fixtures.sip()
def test_associate_with_another_endpoint_when_already_associated(line, sip1, sip2):
    with a.line_endpoint_sip(line, sip1):
        response = confd.lines(line['id']).endpoints.sip(sip2['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.line()
@fixtures.line()
@fixtures.sip()
def test_associate_multiple_lines_to_sip(line1, line2, sip):
    with a.line_endpoint_sip(line1, sip):
        response = confd.lines(line2['id']).endpoints.sip(sip['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.line()
@fixtures.trunk()
@fixtures.sip()
def test_associate_when_trunk_already_associated(line, trunk, sip):
    with a.trunk_endpoint_sip(trunk, sip):
        response = confd.lines(line['id']).endpoints.sip(sip['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.line(context='main-internal')
@fixtures.line(context='sub-internal')
@fixtures.sip(wazo_tenant=MAIN_TENANT)
@fixtures.sip(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(_, __, main_line, sub_line, main_sip, sub_sip):
    response = confd.lines(main_line['id']).endpoints.sip(sub_sip['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('Line'))

    response = confd.lines(sub_line['id']).endpoints.sip(main_sip['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('SIPEndpoint'))

    response = confd.lines(main_line['id']).endpoints.sip(sub_sip['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())


@fixtures.line()
@fixtures.sip()
def test_dissociate(line, sip):
    with a.line_endpoint_sip(line, sip, check=False):
        response = confd.lines(line['id']).endpoints.sip(sip['id']).delete()
        response.assert_deleted()


@fixtures.line()
@fixtures.sip()
def test_dissociate_when_not_associated(line, sip):
    response = confd.lines(line['id']).endpoints.sip(sip['id']).delete()
    response.assert_deleted()


@fixtures.line()
@fixtures.sip()
@fixtures.user()
def test_dissociate_when_associated_to_user(line, sip, user):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line):
        response = confd.lines(line['id']).endpoints.sip(sip['id']).delete()
        response.assert_match(400, e.resource_associated('Line', 'User'))


@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_dissociate_when_associated_to_extension(line, sip, extension):
    with a.line_endpoint_sip(line, sip), a.line_extension(line, extension):
        response = confd.lines(line['id']).endpoints.sip(sip['id']).delete()
        response.assert_match(400, e.resource_associated('Line', 'Extension'))


@fixtures.line()
@fixtures.sip()
def test_get_endpoint_sip_relation(line, sip):
    expected = has_entries(
        endpoint_sip=has_entries(id=sip['id'],
                                 username=sip['username'])
    )

    with a.line_endpoint_sip(line, sip):
        response = confd.lines(line['id']).get()
        assert_that(response.item, expected)


@fixtures.line()
@fixtures.sip()
def test_get_line_relation(line, sip):
    expected = has_entries(
        line=has_entries(id=line['id'])
    )

    with a.line_endpoint_sip(line, sip):
        response = confd.endpoints.sip(sip['id']).get()
        assert_that(response.item, expected)


@fixtures.line()
@fixtures.sip()
def test_delete_endpoint_dissociates_line(line, sip):
    with a.line_endpoint_sip(line, sip, check=False):
        response = confd.endpoints.sip(sip['id']).delete()
        response.assert_deleted()

        response = confd.lines(line['id']).endpoints.sip.get()
        response.assert_status(404)
