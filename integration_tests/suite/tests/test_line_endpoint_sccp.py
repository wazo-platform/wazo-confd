# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from hamcrest import assert_that, has_entries

from test_api import scenarios as s
from test_api import confd
from test_api import errors as e
from test_api import fixtures
from test_api import associations as a


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
                                                'sccp_id': sccp['id']}))


@fixtures.line()
@fixtures.sccp()
def test_get_line_associated_to_a_sccp_endpoint(line, sccp):
    response = confd.endpoints.sccp(sccp['id']).lines.get()
    response.assert_status(404)

    with a.line_endpoint_sccp(line, sccp):
        response = confd.endpoints.sccp(sccp['id']).lines.get()
        assert_that(response.item, has_entries({'line_id': line['id'],
                                                'sccp_id': sccp['id']}))


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
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.line()
@fixtures.sccp()
@fixtures.sccp()
def test_associate_with_another_endpoint_when_already_associated(line, sccp1, sccp2):
    with a.line_endpoint_sccp(line, sccp1):
        response = confd.lines(line['id']).endpoints.sccp(sccp2['id']).put()
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
    response.assert_status(400)


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
def test_delete_endpoint_dissociates_line(line, sccp):
    with a.line_endpoint_sccp(line, sccp, check=False):
        response = confd.endpoints.sccp(sccp['id']).delete()
        response.assert_deleted()

        response = confd.lines(line['id']).endpoints.sccp.get()
        response.assert_status(404)
