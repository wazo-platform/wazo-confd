# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    equal_to,
    has_entries
)

from . import confd
from ..helpers import scenarios as s
from ..helpers import fixtures
from ..helpers.helpers.destination import invalid_destinations, valid_destinations


FAKE_ID = 999999999


def test_get_errors():
    fake_group = confd.groups(FAKE_ID).fallbacks.get
    s.check_resource_not_found(fake_group, 'Group')


def test_put_errors():
    with fixtures.group() as group:
        fake_group = confd.groups(FAKE_ID).fallbacks.put
        s.check_resource_not_found(fake_group, 'Group')

        url = confd.groups(group['id']).fallbacks.put
        error_checks(url)



def error_checks(url):
    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'noanswer_destination', destination)


def test_get():
    with fixtures.group() as group:
        response = confd.groups(group['id']).fallbacks.get()
        assert_that(response.item, has_entries(noanswer_destination=None))



def test_get_all_parameters():
    with fixtures.group() as group:
        parameters = {'noanswer_destination': {'type': 'none'}}
        confd.groups(group['id']).fallbacks.put(parameters).assert_updated()
        response = confd.groups(group['id']).fallbacks.get()
        assert_that(response.item, equal_to(parameters))



def test_edit():
    with fixtures.group() as group:
        response = confd.groups(group['id']).fallbacks.put({})
        response.assert_updated()



def test_edit_with_all_parameters():
    with fixtures.group() as group:
        parameters = {'noanswer_destination': {'type': 'none'}}
        response = confd.groups(group['id']).fallbacks.put(parameters)
        response.assert_updated()



def test_edit_to_none():
    with fixtures.group() as group:
        parameters = {'noanswer_destination': {'type': 'none'}}
        confd.groups(group['id']).fallbacks.put(parameters).assert_updated()

        response = confd.groups(group['id']).fallbacks.put(noanswer_destination=None)
        response.assert_updated

        response = confd.groups(group['id']).fallbacks.get()
        assert_that(response.item, has_entries(noanswer_destination=None))


def test_valid_destinations():
    with fixtures.group() as group, \
            fixtures.meetme() as meetme, \
            fixtures.ivr() as ivr, \
            fixtures.group() as group2, \
            fixtures.outcall() as outcall, \
            fixtures.queue() as queue, \
            fixtures.switchboard() as switchboard, \
            fixtures.user() as user, \
            fixtures.voicemail() as voicemail, \
            fixtures.conference() as conference, \
            fixtures.skill_rule() as skill_rule, \
            fixtures.application() as application:

        destinations = (meetme, ivr, group2, outcall, queue, switchboard, user,
                        voicemail, conference, skill_rule, application)
        for destination in valid_destinations(*destinations):
            _update_group_fallbacks_with_destination(group['id'], destination)


def _update_group_fallbacks_with_destination(group_id, destination):
    response = confd.groups(group_id).fallbacks.put(noanswer_destination=destination)
    response.assert_updated()
    response = confd.groups(group_id).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=has_entries(**destination)))


def test_nonexistent_destinations():
    with fixtures.group() as group:
        meetme = ivr = dest_group = outcall = queue = user = voicemail = conference = skill_rule = {'id': 99999999}
        switchboard = application = {'uuid': '00000000-0000-0000-0000-000000000000'}
        for destination in valid_destinations(meetme, ivr, dest_group, outcall, queue, switchboard,
                                              user, voicemail, conference, skill_rule, application):
            if destination['type'] in ('meetme',
                                       'ivr',
                                       'group',
                                       'outcall',
                                       'queue',
                                       'switchboard',
                                       'user',
                                       'voicemail',
                                       'conference'):
                _update_user_fallbacks_with_nonexistent_destination(group['id'], destination)

            if destination['type'] == 'application' and destination['application'] == 'custom':
                _update_user_fallbacks_with_nonexistent_destination(group['id'], destination)



def _update_user_fallbacks_with_nonexistent_destination(group_id, destination):
    response = confd.groups(group_id).fallbacks.put(noanswer_destination=destination)
    response.assert_status(400)


def test_bus_events():
    with fixtures.group() as group:
        url = confd.groups(group['id']).fallbacks.put
        s.check_bus_event('config.groups.fallbacks.edited', url)



def test_get_fallbacks_relation():
    with fixtures.group() as group:
        confd.groups(group['id']).fallbacks.put(noanswer_destination={'type': 'none'}).assert_updated
        response = confd.groups(group['id']).get()
        assert_that(response.item, has_entries(
            fallbacks=has_entries(noanswer_destination=has_entries(type='none'))
        ))

