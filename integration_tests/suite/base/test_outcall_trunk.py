# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
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


@fixtures.outcall()
@fixtures.trunk()
def test_associate_errors(outcall, trunk):
    response = confd.outcalls(FAKE_ID).trunks.put(trunks=[trunk])
    response.assert_status(404)

    url = confd.outcalls(outcall['id']).trunks().put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'trunks', 123
    yield s.check_bogus_field_returns_error, url, 'trunks', None
    yield s.check_bogus_field_returns_error, url, 'trunks', True
    yield s.check_bogus_field_returns_error, url, 'trunks', 'string'
    yield s.check_bogus_field_returns_error, url, 'trunks', [123]
    yield s.check_bogus_field_returns_error, url, 'trunks', [None]
    yield s.check_bogus_field_returns_error, url, 'trunks', ['string']
    yield s.check_bogus_field_returns_error, url, 'trunks', [{}]
    yield s.check_bogus_field_returns_error, url, 'trunks', [{'id': None}]
    yield s.check_bogus_field_returns_error, url, 'trunks', [{'id': 'string'}]
    yield s.check_bogus_field_returns_error, url, 'trunks', [{'id': 1}, {'id': None}]
    yield s.check_bogus_field_returns_error, url, 'trunks', [{'not_id': 123}]
    yield s.check_bogus_field_returns_error, url, 'trunks', [{'id': FAKE_ID}]


@fixtures.outcall()
@fixtures.trunk()
def test_associate(outcall, trunk):
    response = confd.outcalls(outcall['id']).trunks().put(trunks=[trunk])
    response.assert_updated()


@fixtures.outcall()
@fixtures.trunk()
@fixtures.trunk()
@fixtures.trunk()
def test_associate_multiple(outcall, trunk1, trunk2, trunk3):
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


@fixtures.outcall()
@fixtures.trunk()
def test_associate_same_trunk(outcall, trunk):
    trunks = [{'id': trunk['id']}, {'id': trunk['id']}]
    response = confd.outcalls(outcall['id']).trunks.put(trunks=trunks)
    response.assert_status(400)


@fixtures.outcall()
@fixtures.trunk()
@fixtures.trunk()
def test_get_trunks_associated_to_outcall(outcall, trunk1, trunk2):
    with a.outcall_trunk(outcall, trunk2, trunk1):
        response = confd.outcalls(outcall['id']).get()
        assert_that(response.item, has_entries(
            trunks=contains(
                has_entries(id=trunk2['id'], endpoint_sip=none(), endpoint_custom=none()),
                has_entries(id=trunk1['id'], endpoint_sip=none(), endpoint_custom=none()),
            )
        ))


@fixtures.outcall()
@fixtures.outcall()
@fixtures.trunk()
def test_get_outcalls_associated_to_trunk(outcall1, outcall2, trunk):
    with a.outcall_trunk(outcall2, trunk), a.outcall_trunk(outcall1, trunk):
        response = confd.trunks(trunk['id']).get()
        assert_that(response.item, has_entries(
            outcalls=contains(
                has_entries(id=outcall2['id'], name=outcall2['name']),
                has_entries(id=outcall1['id'], name=outcall1['name']),
            )
        ))


@fixtures.outcall(wazo_tenant=MAIN_TENANT)
@fixtures.outcall(wazo_tenant=SUB_TENANT)
@fixtures.trunk(wazo_tenant=MAIN_TENANT)
@fixtures.trunk(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_outcall, sub_outcall, main_trunk, sub_trunk):
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


@fixtures.outcall()
@fixtures.trunk()
@fixtures.trunk()
def test_dissociate(outcall, trunk1, trunk2):
    with a.outcall_trunk(outcall, trunk1, trunk2):
        response = confd.outcalls(outcall['id']).trunks.put(trunks=[])
        response.assert_updated()


@fixtures.outcall()
@fixtures.trunk()
@fixtures.trunk()
def test_delete_outcall_when_outcall_and_trunk_associated(outcall, trunk1, trunk2):
    with a.outcall_trunk(outcall, trunk1, trunk2, check=False):
        confd.outcalls(outcall['id']).delete().assert_deleted()

        deleted_outcall = confd.outcalls(outcall['id']).get
        yield s.check_resource_not_found, deleted_outcall, 'Outcall'

        response = confd.trunks(trunk1['id']).get()
        yield assert_that, response.item['outcalls'], empty()

        response = confd.trunks(trunk2['id']).get()
        yield assert_that, response.item['outcalls'], empty()


@fixtures.outcall()
@fixtures.outcall()
@fixtures.trunk()
def test_delete_trunk_when_outcall_and_trunk_associated(outcall1, outcall2, trunk):
    with a.outcall_trunk(outcall1, trunk, check=False), a.outcall_trunk(outcall2, trunk, check=False):
        confd.trunks(trunk['id']).delete().assert_deleted()

        deleted_trunk = confd.trunks(trunk['id']).get
        yield s.check_resource_not_found, deleted_trunk, 'Trunk'

        response = confd.outcalls(outcall1['id']).get()
        yield assert_that, response.item['trunks'], empty()

        response = confd.outcalls(outcall2['id']).get()
        yield assert_that, response.item['trunks'], empty()
