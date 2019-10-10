# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, equal_to, has_entries

from . import confd
from ..helpers import scenarios as s
from ..helpers import fixtures
from ..helpers.helpers.destination import invalid_destinations, valid_destinations


FAKE_ID = 999999999


def test_get_errors():
    fake_group = confd.groups(FAKE_ID).fallbacks.get
    yield s.check_resource_not_found, fake_group, 'Group'


@fixtures.group()
def test_put_errors(group):
    fake_group = confd.groups(FAKE_ID).fallbacks.put
    yield s.check_resource_not_found, fake_group, 'Group'

    url = confd.groups(group['id']).fallbacks.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    for destination in invalid_destinations():
        yield s.check_bogus_field_returns_error, url, 'noanswer_destination', destination


@fixtures.group()
def test_get(group):
    response = confd.groups(group['id']).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=None))


@fixtures.group()
def test_get_all_parameters(group):
    parameters = {'noanswer_destination': {'type': 'none'}}
    confd.groups(group['id']).fallbacks.put(parameters).assert_updated()
    response = confd.groups(group['id']).fallbacks.get()
    assert_that(response.item, equal_to(parameters))


@fixtures.group()
def test_edit(group):
    response = confd.groups(group['id']).fallbacks.put({})
    response.assert_updated()


@fixtures.group()
def test_edit_with_all_parameters(group):
    parameters = {'noanswer_destination': {'type': 'none'}}
    response = confd.groups(group['id']).fallbacks.put(parameters)
    response.assert_updated()


@fixtures.group()
def test_edit_to_none(group):
    parameters = {'noanswer_destination': {'type': 'none'}}
    confd.groups(group['id']).fallbacks.put(parameters).assert_updated()

    response = confd.groups(group['id']).fallbacks.put(noanswer_destination=None)
    response.assert_updated

    response = confd.groups(group['id']).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=None))


@fixtures.group()
@fixtures.meetme()
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
def test_valid_destinations(group, *destinations):
    for destination in valid_destinations(*destinations):
        yield _update_group_fallbacks_with_destination, group['id'], destination


def _update_group_fallbacks_with_destination(group_id, destination):
    response = confd.groups(group_id).fallbacks.put(noanswer_destination=destination)
    response.assert_updated()
    response = confd.groups(group_id).fallbacks.get()
    assert_that(
        response.item, has_entries(noanswer_destination=has_entries(**destination))
    )


@fixtures.group()
def test_nonexistent_destinations(group):
    meetme = (
        ivr
    ) = dest_group = outcall = queue = user = voicemail = conference = skill_rule = {
        'id': 99999999
    }
    switchboard = application = {'uuid': '00000000-0000-0000-0000-000000000000'}
    for destination in valid_destinations(
        meetme,
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
    ):
        if destination['type'] in (
            'meetme',
            'ivr',
            'group',
            'outcall',
            'queue',
            'switchboard',
            'user',
            'voicemail',
            'conference',
        ):
            yield _update_user_fallbacks_with_nonexistent_destination, group[
                'id'
            ], destination

        if (
            destination['type'] == 'application'
            and destination['application'] == 'custom'
        ):
            yield _update_user_fallbacks_with_nonexistent_destination, group[
                'id'
            ], destination


def _update_user_fallbacks_with_nonexistent_destination(group_id, destination):
    response = confd.groups(group_id).fallbacks.put(noanswer_destination=destination)
    response.assert_status(400)


@fixtures.group()
def test_bus_events(group):
    url = confd.groups(group['id']).fallbacks.put
    yield s.check_bus_event, 'config.groups.fallbacks.edited', url


@fixtures.group()
def test_get_fallbacks_relation(group):
    confd.groups(group['id']).fallbacks.put(
        noanswer_destination={'type': 'none'}
    ).assert_updated
    response = confd.groups(group['id']).get()
    assert_that(
        response.item,
        has_entries(
            fallbacks=has_entries(noanswer_destination=has_entries(type='none'))
        ),
    )
