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
from test_api import helpers as h


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
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.line()
@fixtures.sip()
@fixtures.sip()
def test_associate_with_another_endpoint_when_already_associated(line, sip1, sip2):
    with a.line_endpoint_sip(line, sip1):
        response = confd.lines(line['id']).endpoints.sip(sip2['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


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
    response.assert_status(400)


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
def test_delete_endpoint_dissociates_line(line, sip):
    with a.line_endpoint_sip(line, sip, check=False):
        response = confd.endpoints.sip(sip['id']).delete()
        response.assert_deleted()

        response = confd.lines(line['id']).endpoints.sip.get()
        response.assert_status(404)
