# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, equal_to, has_entries

from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.helpers.destination import invalid_destinations, valid_destinations
from . import confd

FAKE_ID = 999999999


def test_get_errors():
    fake_queue = confd.queues(FAKE_ID).fallbacks.get
    s.check_resource_not_found(fake_queue, 'Queue')


@fixtures.queue()
@fixtures.user()
def test_put_errors(queue, user):
    fake_queue = confd.queues(FAKE_ID).fallbacks.put
    s.check_resource_not_found(fake_queue, 'Queue')

    url = confd.queues(queue['id']).fallbacks
    error_checks(url.put, user)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url, user):
    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'noanswer_destination', destination)
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


@fixtures.queue()
def test_get(queue):
    response = confd.queues(queue['id']).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=None))


@fixtures.queue()
def test_get_all_parameters(queue):
    parameters = {
        'noanswer_destination': {'type': 'none'},
        'busy_destination': {'type': 'none'},
        'congestion_destination': {'type': 'none'},
        'fail_destination': {'type': 'none'},
    }
    confd.queues(queue['id']).fallbacks.put(parameters).assert_updated()
    response = confd.queues(queue['id']).fallbacks.get()
    assert_that(response.item, equal_to(parameters))


@fixtures.queue()
def test_edit(queue):
    response = confd.queues(queue['id']).fallbacks.put({})
    response.assert_updated()


@fixtures.queue()
def test_edit_with_all_parameters(queue):
    parameters = {
        'noanswer_destination': {'type': 'none'},
        'busy_destination': {'type': 'none'},
        'congestion_destination': {'type': 'none'},
        'fail_destination': {'type': 'none'},
    }
    response = confd.queues(queue['id']).fallbacks.put(parameters)
    response.assert_updated()


@fixtures.queue()
def test_edit_to_none(queue):
    parameters = {
        'noanswer_destination': {'type': 'none'},
        'busy_destination': {'type': 'none'},
        'congestion_destination': {'type': 'none'},
        'fail_destination': {'type': 'none'},
    }
    confd.queues(queue['id']).fallbacks.put(parameters).assert_updated()

    response = confd.queues(queue['id']).fallbacks.put(
        noanswer_destination=None,
        busy_destination=None,
        congestion_destination=None,
        fail_destination=None,
    )
    response.assert_updated

    response = confd.queues(queue['id']).fallbacks.get()
    assert_that(
        response.item,
        has_entries(
            noanswer_destination=None,
            busy_destination=None,
            congestion_destination=None,
            fail_destination=None,
        ),
    )


@fixtures.queue()
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
def test_valid_destinations(queue, *destinations):
    for destination in valid_destinations(*destinations):
        _update_queue_fallbacks_with_destination(queue['id'], destination)


def _update_queue_fallbacks_with_destination(queue_id, destination):
    response = confd.queues(queue_id).fallbacks.put(noanswer_destination=destination)
    response.assert_updated()
    response = confd.queues(queue_id).fallbacks.get()
    assert_that(
        response.item, has_entries(noanswer_destination=has_entries(**destination))
    )


@fixtures.queue()
@fixtures.moh()
def test_nonexistent_destinations(queue, moh):
    ivr = group = outcall = dest_queue = user = voicemail = conference = skill_rule = {
        'id': 99999999
    }
    switchboard = application = {'uuid': '00000000-0000-0000-0000-000000000000'}
    for destination in valid_destinations(
        ivr,
        group,
        outcall,
        dest_queue,
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
                queue['id'], destination
            )

        if (
            destination['type'] == 'application'
            and destination['application'] == 'custom'
        ):
            _update_user_fallbacks_with_nonexistent_destination(
                queue['id'], destination
            )


def _update_user_fallbacks_with_nonexistent_destination(queue_id, destination):
    response = confd.queues(queue_id).fallbacks.put(noanswer_destination=destination)
    response.assert_status(400)


@fixtures.queue()
def test_bus_events(queue):
    url = confd.queues(queue['id']).fallbacks.put
    headers = {'tenant_uuid': queue['tenant_uuid']}

    s.check_event('queue_fallback_edited', headers, url)
