# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    empty,
    has_entries,
    none,
)

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)

FAKE_ID = 999999999


def test_associate_errors():
    with fixtures.outcall() as outcall, fixtures.trunk() as trunk:
        response = confd.outcalls(FAKE_ID).trunks.put(trunks=[trunk])
        response.assert_status(404)

        url = confd.outcalls(outcall['id']).trunks().put
        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'trunks', 123)
    s.check_bogus_field_returns_error(url, 'trunks', None)
    s.check_bogus_field_returns_error(url, 'trunks', True)
    s.check_bogus_field_returns_error(url, 'trunks', 'string')
    s.check_bogus_field_returns_error(url, 'trunks', [123])
    s.check_bogus_field_returns_error(url, 'trunks', [None])
    s.check_bogus_field_returns_error(url, 'trunks', ['string'])
    s.check_bogus_field_returns_error(url, 'trunks', [{}])
    s.check_bogus_field_returns_error(url, 'trunks', [{'id': None}])
    s.check_bogus_field_returns_error(url, 'trunks', [{'id': 'string'}])
    s.check_bogus_field_returns_error(url, 'trunks', [{'id': 1}, {'id': None}])
    s.check_bogus_field_returns_error(url, 'trunks', [{'not_id': 123}])
    s.check_bogus_field_returns_error(url, 'trunks', [{'id': FAKE_ID}])


def test_associate():
    with fixtures.outcall() as outcall, fixtures.trunk() as trunk:
        response = confd.outcalls(outcall['id']).trunks().put(trunks=[trunk])
        response.assert_updated()



def test_associate_multiple():
    with fixtures.outcall() as outcall, fixtures.trunk() as trunk1, fixtures.trunk() as trunk2, fixtures.trunk() as trunk3:
        response = confd.outcalls(outcall['id']).trunks.put(trunks=[trunk2, trunk3, trunk1])
        response.assert_updated()

        response = confd.outcalls(outcall['id']).get()
        assert_that(response.item, has_entries(
            trunks=contains(
                has_entries(id=trunk2['id']),
                has_entries(id=trunk3['id']),
                has_entries(id=trunk1['id']),
            )
        ))



def test_associate_same_trunk():
    with fixtures.outcall() as outcall, fixtures.trunk() as trunk:
        trunks = [{'id': trunk['id']}, {'id': trunk['id']}]
        response = confd.outcalls(outcall['id']).trunks.put(trunks=trunks)
        response.assert_status(400)



def test_get_trunks_associated_to_outcall():
    with fixtures.outcall() as outcall, fixtures.trunk() as trunk1, fixtures.trunk() as trunk2:
        with a.outcall_trunk(outcall, trunk2, trunk1):
            response = confd.outcalls(outcall['id']).get()
            assert_that(response.item, has_entries(
                trunks=contains(
                    has_entries(id=trunk2['id'], endpoint_sip=none(), endpoint_custom=none()),
                    has_entries(id=trunk1['id'], endpoint_sip=none(), endpoint_custom=none()),
                )
            ))


def test_get_outcalls_associated_to_trunk():
    with fixtures.outcall() as outcall1, fixtures.outcall() as outcall2, fixtures.trunk() as trunk:
        with a.outcall_trunk(outcall2, trunk), a.outcall_trunk(outcall1, trunk):
            response = confd.trunks(trunk['id']).get()
            assert_that(response.item, has_entries(
                outcalls=contains(
                    has_entries(id=outcall2['id'], name=outcall2['name']),
                    has_entries(id=outcall1['id'], name=outcall1['name']),
                )
            ))


def test_associate_multi_tenant():
    with fixtures.outcall(wazo_tenant=MAIN_TENANT) as main_outcall, fixtures.outcall(wazo_tenant=SUB_TENANT) as sub_outcall, fixtures.trunk(wazo_tenant=MAIN_TENANT) as main_trunk, fixtures.trunk(wazo_tenant=SUB_TENANT) as sub_trunk:
        response = confd.outcalls(main_outcall['id']).trunks.put(
            trunks=[{'id': main_trunk['id']}],
            wazo_tenant=SUB_TENANT,
        )
        response.assert_match(404, e.not_found('Outcall'))

        response = confd.outcalls(sub_outcall['id']).trunks.put(
            trunks=[{'id': main_trunk['id']}],
            wazo_tenant=SUB_TENANT,
        )
        response.assert_match(400, e.not_found('Trunk'))

        response = confd.outcalls(main_outcall['id']).trunks.put(
            trunks=[{'id': sub_trunk['id']}],
            wazo_tenant=MAIN_TENANT,
        )
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.outcall() as outcall, fixtures.trunk() as trunk1, fixtures.trunk() as trunk2:
        with a.outcall_trunk(outcall, trunk1, trunk2):
            response = confd.outcalls(outcall['id']).trunks.put(trunks=[])
            response.assert_updated()


def test_delete_outcall_when_outcall_and_trunk_associated():
    with fixtures.outcall() as outcall, fixtures.trunk() as trunk1, fixtures.trunk() as trunk2:
        with a.outcall_trunk(outcall, trunk1, trunk2, check=False):
            confd.outcalls(outcall['id']).delete().assert_deleted()

            deleted_outcall = confd.outcalls(outcall['id']).get
            s.check_resource_not_found(deleted_outcall, 'Outcall')

            response = confd.trunks(trunk1['id']).get()
            assert_that(response.item['outcalls'], empty())

            response = confd.trunks(trunk2['id']).get()
            assert_that(response.item['outcalls'], empty())


def test_delete_trunk_when_outcall_and_trunk_associated():
    with fixtures.outcall() as outcall1, fixtures.outcall() as outcall2, fixtures.trunk() as trunk:
        with a.outcall_trunk(outcall1, trunk, check=False), a.outcall_trunk(outcall2, trunk, check=False):
            confd.trunks(trunk['id']).delete().assert_deleted()

            deleted_trunk = confd.trunks(trunk['id']).get
            s.check_resource_not_found(deleted_trunk, 'Trunk')

            response = confd.outcalls(outcall1['id']).get()
            assert_that(response.item['trunks'], empty())

            response = confd.outcalls(outcall2['id']).get()
            assert_that(response.item['trunks'], empty())
