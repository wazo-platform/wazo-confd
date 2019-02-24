# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
    empty,
    has_entries,
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

FAKE_ID = 99999999


@fixtures.call_pickup()
@fixtures.group()
def test_associate_errors(call_pickup, group):
    response = confd.callpickups(FAKE_ID).targets.groups.put(groups=[group])
    response.assert_status(404)

    url = confd.callpickups(call_pickup['id']).targets.groups.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'groups', 123
    yield s.check_bogus_field_returns_error, url, 'groups', None
    yield s.check_bogus_field_returns_error, url, 'groups', True
    yield s.check_bogus_field_returns_error, url, 'groups', 'string'
    yield s.check_bogus_field_returns_error, url, 'groups', [123]
    yield s.check_bogus_field_returns_error, url, 'groups', [None]
    yield s.check_bogus_field_returns_error, url, 'groups', ['string']
    yield s.check_bogus_field_returns_error, url, 'groups', [{}]
    yield s.check_bogus_field_returns_error, url, 'groups', [{'id': None}]
    yield s.check_bogus_field_returns_error, url, 'groups', [{'id': 1}, {'id': None}]
    yield s.check_bogus_field_returns_error, url, 'groups', [{'not_id': 123}]
    yield s.check_bogus_field_returns_error, url, 'groups', [{'id': FAKE_ID}]


@fixtures.call_pickup()
@fixtures.group()
def test_associate(call_pickup, group):
    response = confd.callpickups(call_pickup['id']).targets.groups.put(groups=[group])
    response.assert_updated()


@fixtures.call_pickup()
@fixtures.group()
@fixtures.group()
@fixtures.group()
def test_associate_multiple(call_pickup, group1, group2, group3):
    response = confd.callpickups(call_pickup['id']).targets.groups.put(groups=[group1, group2, group3])
    response.assert_updated()

    response = confd.callpickups(call_pickup['id']).get()
    assert_that(response.item, has_entries(
        targets=has_entries(groups=contains_inanyorder(
            has_entries(id=group1['id']),
            has_entries(id=group2['id']),
            has_entries(id=group3['id'])
        ))
    ))


@fixtures.call_pickup()
@fixtures.group()
def test_associate_same_group(call_pickup, group):
    response = confd.callpickups(call_pickup['id']).targets.groups.put(groups=[group, group])
    response.assert_status(400)


@fixtures.call_pickup(wazo_tenant=MAIN_TENANT)
@fixtures.call_pickup(wazo_tenant=SUB_TENANT)
@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_call_pickup, sub_call_pickup, main_group, sub_group):
    response = (
        confd.callpickups(main_call_pickup['id'])
        .targets.groups(groups=[sub_group])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('CallPickup'))

    response = (
        confd.callpickups(sub_call_pickup['id'])
        .targets.groups(groups=[main_group])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(400, e.not_found('Group'))

    response = (
        confd.callpickups(sub_call_pickup['id'])
        .interceptors.groups(groups=[main_group])
        .put(wazo_tenant=MAIN_TENANT)
    )
    response.assert_match(400, e.different_tenant())


@fixtures.call_pickup()
@fixtures.group()
@fixtures.group()
def test_get_groups_associated_to_call_pickup(call_pickup, group1, group2):
    with a.call_pickup_target_group(call_pickup, group1, group2):
        response = confd.callpickups(call_pickup['id']).get()
        assert_that(response.item, has_entries(
            targets=has_entries(groups=contains_inanyorder(
                has_entries(
                    id=group1['id'],
                    name=group1['name'],
                ),
                has_entries(
                    id=group2['id'],
                    name=group2['name'],
                ),
            ))
        ))


@fixtures.call_pickup()
@fixtures.group()
def test_dissociate(call_pickup, group):
    with a.call_pickup_target_group(call_pickup, group):
        response = confd.callpickups(call_pickup['id']).targets.groups.put(groups=[])
        response.assert_updated()


@fixtures.call_pickup()
@fixtures.group()
@fixtures.group()
def test_delete_call_pickup_when_call_pickup_and_group_associated(call_pickup, group1, group2):
    with a.call_pickup_target_group(call_pickup, group1, group2, check=False):
        confd.callpickups(call_pickup['id']).delete().assert_deleted()

        deleted_call_pickup = confd.callpickups(call_pickup['id']).get
        yield s.check_resource_not_found, deleted_call_pickup, 'CallPickup'

        # When the relation will be added,
        # we should check if groups have the key.callpickups to empty


@fixtures.call_pickup()
@fixtures.call_pickup()
@fixtures.group()
def test_delete_group_when_call_pickup_and_group_associated(call_pickup1, call_pickup2, group):
    with a.call_pickup_target_group(call_pickup1, group, check=False), \
            a.call_pickup_target_group(call_pickup2, group, check=False):
        confd.groups(group['id']).delete().assert_deleted()

        response = confd.callpickups(call_pickup1['id']).get()
        yield assert_that, response.item['targets']['groups'], empty()

        response = confd.callpickups(call_pickup2['id']).get()
        yield assert_that, response.item['targets']['groups'], empty()


@fixtures.call_pickup()
@fixtures.group()
def test_bus_events(call_pickup, group):
    url = confd.callpickups(call_pickup['id']).targets.groups.put
    body = {'groups': [group]}
    yield s.check_bus_event, 'config.callpickups.targets.groups.updated', url, body
