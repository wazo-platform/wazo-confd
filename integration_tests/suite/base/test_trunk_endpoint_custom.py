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
@fixtures.custom()
def test_associate_errors(trunk, custom):
    fake_trunk = confd.trunks(FAKE_ID).endpoints.custom(custom['id']).put
    fake_custom = confd.trunks(trunk['id']).endpoints.custom(FAKE_ID).put

    yield s.check_resource_not_found, fake_trunk, 'Trunk'
    yield s.check_resource_not_found, fake_custom, 'CustomEndpoint'


@fixtures.trunk()
@fixtures.custom()
def test_dissociate_errors(trunk, custom):
    fake_trunk_custom = confd.trunks(trunk['id']).endpoints.custom(custom['id']).delete
    fake_trunk = confd.trunks(FAKE_ID).endpoints.custom(custom['id']).delete
    fake_custom = confd.trunks(trunk['id']).endpoints.custom(FAKE_ID).delete

    yield s.check_resource_not_found, fake_trunk, 'Trunk'
    yield s.check_resource_not_found, fake_custom, 'CustomEndpoint'
    yield fake_trunk_custom().assert_status, 400


def test_get_errors():
    fake_trunk = confd.trunks(FAKE_ID).endpoints.custom.get
    fake_custom = confd.endpoints.custom(FAKE_ID).trunks.get

    yield s.check_resource_not_found, fake_trunk, 'Trunk'
    yield s.check_resource_not_found, fake_custom, 'CustomEndpoint'


@fixtures.trunk()
@fixtures.custom()
def test_associate(trunk, custom):
    response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).put()
    response.assert_updated()


@fixtures.trunk()
@fixtures.custom()
def test_associate_already_associated(trunk, custom):
    with a.trunk_endpoint_custom(trunk, custom):
        response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.custom()
@fixtures.custom()
def test_associate_multiple_custom_to_trunk(trunk, custom1, custom2):
    with a.trunk_endpoint_custom(trunk, custom1):
        response = confd.trunks(trunk['id']).endpoints.custom(custom2['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.trunk()
@fixtures.custom()
def test_associate_multiple_trunks_to_custom(trunk1, trunk2, custom):
    with a.trunk_endpoint_custom(trunk1, custom):
        response = confd.trunks(trunk2['id']).endpoints.custom(custom['id']).put()
        response.assert_match(400, e.resource_associated('Trunk', 'Endpoint'))


@fixtures.trunk()
@fixtures.line()
@fixtures.custom()
def test_associate_when_line_already_associated(trunk, line, custom):
    with a.line_endpoint_custom(line, custom):
        response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).put()
        response.assert_match(400, e.resource_associated('Line', 'Endpoint'))


@fixtures.trunk()
@fixtures.custom()
def test_get_endpoint_associated_to_trunk(trunk, custom):
    expected = has_entries({'trunk_id': trunk['id'],
                            'endpoint': 'custom',
                            'endpoint_id': custom['id']})

    with a.trunk_endpoint_custom(trunk, custom):
        response = confd.trunks(trunk['id']).endpoints.custom.get()
        assert_that(response.item, expected)


@fixtures.trunk()
@fixtures.custom()
def test_get_trunk_associated_to_endpoint(trunk, custom):
    expected = has_entries({'trunk_id': trunk['id'],
                            'endpoint': 'custom',
                            'endpoint_id': custom['id']})

    with a.trunk_endpoint_custom(trunk, custom):
        response = confd.endpoints.custom(custom['id']).trunks.get()
        assert_that(response.item, expected)


@fixtures.trunk()
def test_get_no_endpoint(trunk):
    response = confd.trunks(trunk['id']).endpoints.custom.get()
    response.assert_match(404, e.not_found('TrunkEndpoint'))


@fixtures.trunk()
@fixtures.custom()
def test_dissociate(trunk, custom):
    with a.trunk_endpoint_custom(trunk, custom, check=False):
        response = confd.trunks(trunk['id']).endpoints.custom(custom['id']).delete()
        response.assert_deleted()


@fixtures.trunk()
@fixtures.custom()
def test_get_endpoint_custom_relation(trunk, custom):
    expected = has_entries({
        'endpoint_custom': has_entries({'interface': custom['interface']})
    })

    with a.trunk_endpoint_custom(trunk, custom):
        response = confd.trunks(trunk['id']).get()
        assert_that(response.item, expected)


@fixtures.trunk()
@fixtures.custom()
def test_get_trunk_relation(trunk, custom):
    expected = has_entries({
        'trunk': has_key('links')
    })

    with a.trunk_endpoint_custom(trunk, custom):
        response = confd.endpoints.custom(custom['id']).get()
        assert_that(response.item, expected)


@fixtures.trunk()
@fixtures.custom()
def test_delete_trunk_when_trunk_and_endpoint_associated(trunk, custom):
    with a.trunk_endpoint_custom(trunk, custom, check=False):
        confd.trunks(trunk['id']).delete().assert_deleted()

        deleted_trunk = confd.trunks(custom['id']).endpoints.custom.get
        deleted_custom = confd.endpoints.custom(custom['id']).trunks.get
        yield s.check_resource_not_found, deleted_trunk, 'Trunk'
        yield s.check_resource_not_found, deleted_custom, 'CustomEndpoint'


@fixtures.trunk()
@fixtures.custom()
def test_delete_custom_when_trunk_and_custom_associated(trunk, custom):
    with a.trunk_endpoint_custom(trunk, custom, check=False):
        confd.endpoints.custom(custom['id']).delete().assert_deleted()

        response = confd.trunks(trunk['id']).endpoints.custom.get()
        response.assert_match(404, e.not_found('TrunkEndpoint'))
