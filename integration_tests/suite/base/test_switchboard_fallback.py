# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, equal_to, has_entries

from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.helpers.destination import invalid_destinations, valid_destinations
from . import confd

FAKE_UUID = '99999999-9999-9999-9999-999999999999'


def test_get_errors():
    fake_switchboard = confd.switchboards(FAKE_UUID).fallbacks.get
    yield s.check_resource_not_found, fake_switchboard, 'Switchboard'


@fixtures.switchboard()
@fixtures.user()
def test_put_errors(switchboard, user):
    fake_switchboard = confd.switchboards(FAKE_UUID).fallbacks.put
    yield s.check_resource_not_found, fake_switchboard, 'Switchboard'

    url = confd.switchboards(switchboard['uuid']).fallbacks.put
    yield from error_checks(url, user)

    url = confd.switchboards(switchboard['uuid']).fallbacks.put
    yield from error_checks(url, user)


def error_checks(url, user):
    for destination in invalid_destinations():
        yield s.check_bogus_field_returns_error, url, 'noanswer_destination', destination
    yield s.check_bogus_field_returns_error, url, 'noanswer_destination', {
        'type': 'user',
        'user_id': user['id'],
        'moh_uuid': '00000000-0000-0000-0000-000000000000',
    }, {}, 'MOH was not found'


@fixtures.switchboard()
def test_get(switchboard):
    response = confd.switchboards(switchboard['uuid']).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=None))

    response = confd.switchboards(switchboard['uuid']).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=None))


@fixtures.switchboard()
def test_get_all_parameters(switchboard):
    parameters = {'noanswer_destination': {'type': 'none'}}
    confd.switchboards(switchboard['uuid']).fallbacks.put(parameters).assert_updated()
    response = confd.switchboards(switchboard['uuid']).fallbacks.get()
    assert_that(response.item, equal_to(parameters))


@fixtures.switchboard()
def test_edit(switchboard):
    response = confd.switchboards(switchboard['uuid']).fallbacks.put({})
    response.assert_updated()

    response = confd.switchboards(switchboard['uuid']).fallbacks.put({})
    response.assert_updated()


@fixtures.switchboard()
def test_edit_with_all_parameters(switchboard):
    parameters = {'noanswer_destination': {'type': 'none'}}
    response = confd.switchboards(switchboard['uuid']).fallbacks.put(parameters)
    response.assert_updated()


@fixtures.switchboard()
def test_edit_to_none(switchboard):
    parameters = {'noanswer_destination': {'type': 'none'}}
    confd.switchboards(switchboard['uuid']).fallbacks.put(parameters).assert_updated()

    response = confd.switchboards(switchboard['uuid']).fallbacks.put(
        noanswer_destination=None
    )
    response.assert_updated

    response = confd.switchboards(switchboard['uuid']).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=None))


@fixtures.switchboard()
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
def test_valid_destinations(switchboard, *destinations):
    for destination in valid_destinations(*destinations):
        yield _update_switchboard_fallbacks_with_destination, switchboard[
            'uuid'
        ], destination


def _update_switchboard_fallbacks_with_destination(switchboard_uuid, destination):
    response = confd.switchboards(switchboard_uuid).fallbacks.put(
        noanswer_destination=destination
    )
    response.assert_updated()
    response = confd.switchboards(switchboard_uuid).fallbacks.get()
    assert_that(
        response.item, has_entries(noanswer_destination=has_entries(**destination))
    )


@fixtures.switchboard()
@fixtures.moh()
def test_nonexistent_destinations(switchboard, moh):
    ivr = group = outcall = queue = user = voicemail = conference = skill_rule = {
        'id': 99999999
    }
    dest_switchboard = application = {'uuid': FAKE_UUID}
    for destination in valid_destinations(
        ivr,
        group,
        outcall,
        queue,
        dest_switchboard,
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
        ) or (
            destination['type'] == 'application'
            and destination['application'] == 'custom'
        ):
            yield _update_user_fallbacks_with_nonexistent_destination, switchboard[
                'uuid'
            ], destination


def _update_user_fallbacks_with_nonexistent_destination(switchboard_uuid, destination):
    response = confd.switchboards(switchboard_uuid).fallbacks.put(
        noanswer_destination=destination
    )
    response.assert_status(400)


@fixtures.switchboard()
def test_bus_events(switchboard):
    url = confd.switchboards(switchboard['uuid']).fallbacks.put
    headers = {
        'tenant_uuid': switchboard['tenant_uuid'],
        'switchboard_uuid': switchboard['uuid'],
    }

    yield s.check_event, 'switchboard_fallback_edited', headers, url


@fixtures.switchboard()
def test_get_fallbacks_relation(switchboard):
    confd.switchboards(switchboard['uuid']).fallbacks.put(
        noanswer_destination={'type': 'none'}
    ).assert_updated
    response = confd.switchboards(switchboard['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            fallbacks=has_entries(noanswer_destination=has_entries(type='none'))
        ),
    )
