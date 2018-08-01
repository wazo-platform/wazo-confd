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


def test_get_errors():
    fake_line = confd.lines(999999999).endpoints.sccp.get
    fake_sccp = confd.endpoints.sccp(999999999).lines.get

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_sccp, 'SCCPEndpoint'


@fixtures.line()
@fixtures.sccp()
def test_get_sccp_endpoint_associated_to_line(line, sccp):
    response = confd.lines(line['id']).endpoints.sccp.get()
    response.assert_status(404)

    with a.line_endpoint_sccp(line, sccp):
        response = confd.lines(line['id']).endpoints.sccp.get()
        assert_that(response.item, has_entries({'line_id': line['id'],
                                                'endpoint_id': sccp['id'],
                                                'endpoint': 'sccp'}))


@fixtures.line()
@fixtures.sccp()
def test_get_sccp_endpoint_after_dissociation(line, sccp):
    h.line_endpoint_sccp.associate(line['id'], sccp['id'])
    h.line_endpoint_sccp.dissociate(line['id'], sccp['id'])

    response = confd.lines(line['id']).endpoints.sccp.get()
    response.assert_status(404)


@fixtures.line()
@fixtures.sccp()
def test_get_line_associated_to_a_sccp_endpoint(line, sccp):
    response = confd.endpoints.sccp(sccp['id']).lines.get()
    response.assert_status(404)

    with a.line_endpoint_sccp(line, sccp):
        response = confd.endpoints.sccp(sccp['id']).lines.get()
        assert_that(response.item, has_entries({'line_id': line['id'],
                                                'endpoint_id': sccp['id'],
                                                'endpoint': 'sccp'}))


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


@fixtures.line()
@fixtures.sccp()
def test_get_endpoint_sccp_relation(line, sccp):
    expected = has_entries(
        endpoint_sccp=has_entries(id=sccp['id'])
    )

    with a.line_endpoint_sccp(line, sccp):
        response = confd.lines(line['id']).get()
        assert_that(response.item, expected)


@fixtures.line()
@fixtures.sccp()
def test_get_line_relation(line, sccp):
    expected = has_entries(
        line=has_entries(id=line['id'])
    )

    with a.line_endpoint_sccp(line, sccp):
        response = confd.endpoints.sccp(sccp['id']).get()
        assert_that(response.item, expected)


@fixtures.line()
@fixtures.sccp()
def test_delete_endpoint_dissociates_line(line, sccp):
    with a.line_endpoint_sccp(line, sccp, check=False):
        response = confd.endpoints.sccp(sccp['id']).delete()
        response.assert_deleted()

        response = confd.lines(line['id']).endpoints.sccp.get()
        response.assert_status(404)
