# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, equal_to, has_entries

from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT
from ..helpers.helpers.destination import invalid_destinations, valid_destinations
from . import confd

FAKE_ID = 999999999


def test_get_errors():
    fake_group = confd.groups(FAKE_ID).fallbacks.get
    s.check_resource_not_found(fake_group, 'Group')


@fixtures.group()
@fixtures.user()
def test_put_errors(group, user):
    fake_group = confd.groups(FAKE_ID).fallbacks.put
    s.check_resource_not_found(fake_group, 'Group')

    url = confd.groups(group['uuid']).fallbacks
    error_checks(url.put, user)
    s.check_missing_body_returns_error(url, 'PUT')

    url = confd.groups(group['id']).fallbacks
    error_checks(url.put, user)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url, user):
    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'noanswer_destination', destination)
        s.check_bogus_field_returns_error(url, 'congestion_destination', destination)
    s.check_bogus_field_returns_error(
        url,
        'noanswer_destination',
        {
            'type': 'user',
            'user_id': user['id'],
            'moh_uuid': '00000000-0000-0000-0000-000000000000',
        },
        {},
        'MOH was not found',
    )
    s.check_bogus_field_returns_error(
        url,
        'congestion_destination',
        {
            'type': 'user',
            'user_id': user['id'],
            'moh_uuid': '00000000-0000-0000-0000-000000000000',
        },
        {},
        'MOH was not found',
    )


@fixtures.group()
def test_get(group):
    response = confd.groups(group['id']).fallbacks.get()
    assert_that(
        response.item,
        has_entries(noanswer_destination=None, congestion_destination=None),
    )

    response = confd.groups(group['uuid']).fallbacks.get()
    assert_that(
        response.item,
        has_entries(noanswer_destination=None, congestion_destination=None),
    )


@fixtures.group()
def test_get_all_parameters(group):
    parameters = {
        'noanswer_destination': {'type': 'none'},
        'congestion_destination': {'type': 'none'},
    }
    confd.groups(group['uuid']).fallbacks.put(parameters).assert_updated()
    response = confd.groups(group['uuid']).fallbacks.get()
    assert_that(response.item, equal_to(parameters))


@fixtures.group()
def test_edit(group):
    response = confd.groups(group['id']).fallbacks.put({})
    response.assert_updated()

    response = confd.groups(group['uuid']).fallbacks.put({})
    response.assert_updated()


@fixtures.group()
def test_edit_with_all_parameters(group):
    parameters = {
        'noanswer_destination': {'type': 'none'},
        'congestion_destination': {'type': 'none'},
    }
    response = confd.groups(group['uuid']).fallbacks.put(parameters)
    response.assert_updated()


@fixtures.group()
def test_edit_to_none(group):
    parameters = {
        'noanswer_destination': {'type': 'none'},
        'congestion_destination': {'type': 'none'},
    }
    confd.groups(group['uuid']).fallbacks.put(parameters).assert_updated()

    response = confd.groups(group['uuid']).fallbacks.put(
        noanswer_destination=None, congestion_destination=None
    )
    response.assert_updated

    response = confd.groups(group['uuid']).fallbacks.get()
    assert_that(
        response.item,
        has_entries(noanswer_destination=None, congestion_destination=None),
    )


@fixtures.group()
@fixtures.ivr()
@fixtures.group()
@fixtures.outcall()
@fixtures.queue()
@fixtures.switchboard()
@fixtures.user()
@fixtures.voicemail()
@fixtures.conference()
@fixtures.skill_rule()
@fixtures.application()
@fixtures.moh()
def test_valid_destinations(group, *destinations):
    for destination in valid_destinations(*destinations):
        _update_group_fallbacks_with_destination(group['uuid'], destination)


def _update_group_fallbacks_with_destination(group_uuid, destination):
    response = confd.groups(group_uuid).fallbacks.put(
        noanswer_destination=destination, congestion_destination=destination
    )
    response.assert_updated()
    response = confd.groups(group_uuid).fallbacks.get()
    assert_that(
        response.item,
        has_entries(
            noanswer_destination=has_entries(**destination),
            congestion_destination=has_entries(**destination),
        ),
    )


@fixtures.group()
@fixtures.moh()
def test_nonexistent_destinations(group, moh):
    ivr = dest_group = outcall = queue = user = voicemail = conference = skill_rule = {
        'id': 99999999
    }
    switchboard = application = {'uuid': '00000000-0000-0000-0000-000000000000'}
    for destination in valid_destinations(
        ivr,
        dest_group,
        outcall,
        queue,
        switchboard,
        user,
        voicemail,
        conference,
        skill_rule,
        application,
        moh,
    ):
        if destination['type'] in (
            'ivr',
            'group',
            'outcall',
            'queue',
            'switchboard',
            'user',
            'voicemail',
            'conference',
        ):
            _update_user_fallbacks_with_nonexistent_destination(
                group['uuid'], destination
            )

        if (
            destination['type'] == 'application'
            and destination['application'] == 'custom'
        ):
            _update_user_fallbacks_with_nonexistent_destination(
                group['uuid'], destination
            )


def _update_user_fallbacks_with_nonexistent_destination(group_uuid, destination):
    response = confd.groups(group_uuid).fallbacks.put(
        noanswer_destination=destination, congestion_destination=destination
    )
    response.assert_status(400)


@fixtures.group()
def test_bus_events(group):
    url = confd.groups(group['uuid']).fallbacks.put
    headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event('group_fallback_edited', headers, url)


@fixtures.group()
def test_get_fallbacks_relation(group):
    confd.groups(group['uuid']).fallbacks.put(
        noanswer_destination={'type': 'none'},
        congestion_destination={'type': 'none'},
    ).assert_updated
    response = confd.groups(group['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            fallbacks=has_entries(
                noanswer_destination=has_entries(type='none'),
                congestion_destination=has_entries(type='none'),
            )
        ),
    )
