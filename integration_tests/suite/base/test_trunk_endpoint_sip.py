# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

from hamcrest import (assert_that,
                      has_entries,
                      has_key)

from test_api import scenarios as s
from test_api import confd
from test_api import errors as e
from test_api import fixtures
from test_api import associations as a


FAKE_ID = 999999999


@fixtures.trunk()
@fixtures.sip()
def test_associate_errors(trunk, sip):
    fake_trunk = confd.trunks(FAKE_ID).endpoints.sip(sip['id']).put
    fake_sip = confd.trunks(trunk['id']).endpoints.sip(FAKE_ID).put

    yield s.check_resource_not_found, fake_trunk, 'Trunk'
    yield s.check_resource_not_found, fake_sip, 'SIPEndpoint'


@fixtures.trunk()
@fixtures.sip()
def test_dissociate_errors(trunk, sip):
    fake_trunk_sip = confd.trunks(trunk['id']).endpoints.sip(sip['id']).delete
    fake_trunk = confd.trunks(FAKE_ID).endpoints.sip(sip['id']).delete
    fake_sip = confd.trunks(trunk['id']).endpoints.sip(FAKE_ID).delete

    yield s.check_resource_not_found, fake_trunk, 'Trunk'
    yield s.check_resource_not_found, fake_sip, 'SIPEndpoint'
    yield fake_trunk_sip().assert_status, 400


def test_get_errors():
    fake_trunk = confd.trunks(FAKE_ID).endpoints.sip.get
    fake_sip = confd.endpoints.sip(FAKE_ID).trunks.get

    yield s.check_resource_not_found, fake_trunk, 'Trunk'
    yield s.check_resource_not_found, fake_sip, 'SIPEndpoint'


@fixtures.trunk()
@fixtures.sip()
def test_associate(trunk, sip):
    response = confd.trunks(trunk['id']).endpoints.sip(sip['id']).put()
    response.assert_updated()


@fixtures.trunk()
@fixtures.sip()
def test_associate_already_associated(trunk, sip):
    with a.trunk_endpoint_sip(trunk, sip):
        response = confd.trunks(trunk['id']).endpoints.sip(sip['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.sip()
@fixtures.sip()
def test_associate_multiple_sip_to_trunk(trunk, sip1, sip2):
    with a.trunk_endpoint_sip(trunk, sip1):
        response = confd.trunks(trunk['id']).endpoints.sip(sip2['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.trunk()
@fixtures.sip()
def test_associate_multiple_trunks_to_sip(trunk1, trunk2, sip):
    with a.trunk_endpoint_sip(trunk1, sip):
        response = confd.trunks(trunk2['id']).endpoints.sip(sip['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.line()
@fixtures.sip()
def test_associate_when_line_already_associated(trunk, line, sip):
    with a.line_endpoint_sip(line, sip):
        response = confd.trunks(trunk['id']).endpoints.sip(sip['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.trunk()
@fixtures.sip()
def test_get_endpoint_associated_to_trunk(trunk, sip):
    expected = has_entries({'trunk_id': trunk['id'],
                            'endpoint': 'sip',
                            'endpoint_id': sip['id']})

    with a.trunk_endpoint_sip(trunk, sip):
        response = confd.trunks(trunk['id']).endpoints.sip.get()
        assert_that(response.item, expected)


@fixtures.trunk()
@fixtures.sip()
def test_get_trunk_associated_to_endpoint(trunk, sip):
    expected = has_entries({'trunk_id': trunk['id'],
                            'endpoint': 'sip',
                            'endpoint_id': sip['id']})

    with a.trunk_endpoint_sip(trunk, sip):
        response = confd.endpoints.sip(sip['id']).trunks.get()
        assert_that(response.item, expected)


@fixtures.trunk()
def test_get_no_endpoint(trunk):
    response = confd.trunks(trunk['id']).endpoints.sip.get()
    response.assert_match(404, e.not_found('TrunkEndpoint'))


@fixtures.trunk()
@fixtures.sip()
def test_dissociate(trunk, sip):
    with a.trunk_endpoint_sip(trunk, sip, check=False):
        response = confd.trunks(trunk['id']).endpoints.sip(sip['id']).delete()
        response.assert_deleted()


@fixtures.trunk()
@fixtures.sip()
def test_get_endpoint_sip_relation(trunk, sip):
    expected = has_entries({
        'endpoint_sip': has_entries({'username': sip['username']}),
    })

    with a.trunk_endpoint_sip(trunk, sip):
        response = confd.trunks(trunk['id']).get()
        assert_that(response.item, expected)


@fixtures.trunk()
@fixtures.sip()
def test_get_trunk_relation(trunk, sip):
    expected = has_entries({
        'trunk': has_key('links')
    })

    with a.trunk_endpoint_sip(trunk, sip):
        response = confd.endpoints.sip(sip['id']).get()
        assert_that(response.item, expected)


@fixtures.trunk()
@fixtures.sip()
def test_delete_trunk_when_trunk_and_endpoint_associated(trunk, sip):
    with a.trunk_endpoint_sip(trunk, sip, check=False):
        confd.trunks(trunk['id']).delete().assert_deleted()

        deleted_trunk = confd.trunks(sip['id']).endpoints.sip.get
        deleted_sip = confd.endpoints.sip(sip['id']).trunks.get
        yield s.check_resource_not_found, deleted_trunk, 'Trunk'
        yield s.check_resource_not_found, deleted_sip, 'SIPEndpoint'


@fixtures.trunk()
@fixtures.sip()
def test_delete_sip_when_trunk_and_sip_associated(trunk, sip):
    with a.trunk_endpoint_sip(trunk, sip, check=False):
        confd.endpoints.sip(sip['id']).delete().assert_deleted()

        response = confd.trunks(trunk['id']).endpoints.sip.get()
        response.assert_match(404, e.not_found('TrunkEndpoint'))
