# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.helpers.destination import invalid_destinations, valid_destinations
from . import confd

FAKE_ID = 999999999


def test_get_errors():
    fake_user = confd.users(FAKE_ID).fallbacks.get
    s.check_resource_not_found(fake_user, 'User')


@fixtures.user()
def test_put_errors(user):
    fake_user = confd.users(FAKE_ID).fallbacks.put
    s.check_resource_not_found(fake_user, 'User')

    url = confd.users(user['uuid']).fallbacks
    error_checks(url.put, user)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url, user):
    destination_types = [
        'noanswer_destination',
        'busy_destination',
        'congestion_destination',
        'fail_destination',
    ]

    for destination_type in destination_types:
        for destination in invalid_destinations():
            s.check_bogus_field_returns_error(url, destination_type, destination)

        s.check_bogus_field_returns_error(
            url,
            destination_type,
            {
                'type': 'user',
                'user_id': user['id'],
                'moh_uuid': '00000000-0000-0000-0000-000000000000',
            },
            {},
            'MOH was not found',
        )


@fixtures.user()
def test_get(user):
    response = confd.users(user['uuid']).fallbacks.get()
    assert_that(
        response.item,
        has_entries(
            noanswer_destination=None,
            busy_destination=None,
            congestion_destination=None,
            fail_destination=None,
        ),
    )


@fixtures.user(
    fallbacks={
        'noanswer_destination': {'type': 'none'},
        'busy_destination': {'type': 'none'},
        'congestion_destination': {'type': 'none'},
        'fail_destination': {'type': 'none'},
    }
)
def test_get_all_parameters(user):
    response = confd.users(user['uuid']).fallbacks.get()
    assert_that(
        response.item,
        has_entries(
            noanswer_destination={'type': 'none'},
            busy_destination={'type': 'none'},
            congestion_destination={'type': 'none'},
            fail_destination={'type': 'none'},
        ),
    )


@fixtures.user()
def test_edit(user):
    response = confd.users(user['uuid']).fallbacks.put({})
    response.assert_updated()


@fixtures.user()
def test_edit_with_all_parameters(user):
    parameters = {
        'noanswer_destination': {'type': 'none'},
        'busy_destination': {'type': 'none'},
        'congestion_destination': {'type': 'none'},
        'fail_destination': {'type': 'none'},
    }
    response = confd.users(user['id']).fallbacks.put(parameters)
    response.assert_updated()


@fixtures.user(
    fallbacks={
        'noanswer_destination': {'type': 'none'},
        'busy_destination': {'type': 'none'},
        'congestion_destination': {'type': 'none'},
        'fail_destination': {'type': 'none'},
    }
)
def test_edit_to_none(user):
    response = confd.users(user['uuid']).fallbacks.put(
        noanswer_destination=None,
        busy_destination=None,
        congestion_destination=None,
        fail_destination=None,
    )
    response.assert_updated

    response = confd.users(user['uuid']).fallbacks.get()
    assert_that(
        response.item,
        has_entries(
            noanswer_destination=None,
            busy_destination=None,
            congestion_destination=None,
            fail_destination=None,
        ),
    )


@fixtures.user()
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
def test_valid_destinations(user, *destinations):
    for destination in valid_destinations(*destinations):
        _update_user_fallbacks_with_destination(user['uuid'], destination)


def _update_user_fallbacks_with_destination(user_id, destination):
    response = confd.users(user_id).fallbacks.put(
        noanswer_destination=destination,
        busy_destination=destination,
        congestion_destination=destination,
        fail_destination=destination,
    )
    response.assert_updated()
    response = confd.users(user_id).fallbacks.get()
    assert_that(
        response.item,
        has_entries(
            noanswer_destination=has_entries(**destination),
            busy_destination=has_entries(**destination),
            congestion_destination=has_entries(**destination),
            fail_destination=has_entries(**destination),
        ),
    )


@fixtures.user()
def test_nonexistent_destinations(user):
    ivr = group = outcall = queue = dest_user = voicemail = conference = skill_rule = {
        'id': 99999999
    }
    moh = switchboard = application = {'uuid': '00000000-0000-0000-0000-000000000000'}
    for destination in valid_destinations(
        ivr,
        group,
        outcall,
        queue,
        switchboard,
        dest_user,
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
                user['uuid'], destination
            )

        if (
            destination['type'] == 'application'
            and destination['application'] == 'custom'
        ):
            _update_user_fallbacks_with_nonexistent_destination(
                user['uuid'], destination
            )


def _update_user_fallbacks_with_nonexistent_destination(user_id, destination):
    response = confd.users(user_id).fallbacks.put(
        noanswer_destination=destination,
        busy_destination=destination,
        congestion_destination=destination,
        fail_destination=destination,
    )
    response.assert_status(400)


@fixtures.user()
def test_bus_events(user):
    url = confd.users(user['uuid']).fallbacks.put
    headers = {'tenant_uuid': user['tenant_uuid']}

    s.check_event('user_fallback_edited', headers, url)


@fixtures.user(
    fallbacks={
        'noanswer_destination': {'type': 'none'},
        'busy_destination': {'type': 'none'},
        'congestion_destination': {'type': 'none'},
        'fail_destination': {'type': 'none'},
    }
)
def test_get_fallbacks_relation(user):
    response = confd.users(user['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            fallbacks=has_entries(
                noanswer_destination=has_entries(type='none'),
                busy_destination=has_entries(type='none'),
                congestion_destination=has_entries(type='none'),
                fail_destination=has_entries(type='none'),
            )
        ),
    )
