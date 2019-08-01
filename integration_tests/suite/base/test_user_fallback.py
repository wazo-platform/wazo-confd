# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from . import confd
from ..helpers import scenarios as s
from ..helpers import fixtures
from ..helpers.helpers.destination import invalid_destinations, valid_destinations

FAKE_ID = 999999999


def test_get_errors():
    fake_user = confd.users(FAKE_ID).fallbacks.get
    s.check_resource_not_found(fake_user, 'User')


def test_put_errors():
    with fixtures.user() as user:
        fake_user = confd.users(FAKE_ID).fallbacks.put
        s.check_resource_not_found(fake_user, 'User')

        url = confd.users(user['uuid']).fallbacks.put
        error_checks(url)



def error_checks(url):
    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'noanswer_destination', destination)
        s.check_bogus_field_returns_error(url, 'busy_destination', destination)
        s.check_bogus_field_returns_error(url, 'congestion_destination', destination)
        s.check_bogus_field_returns_error(url, 'fail_destination', destination)


def test_get():
    with fixtures.user() as user:
        response = confd.users(user['uuid']).fallbacks.get()
        assert_that(response.item, has_entries(noanswer_destination=None,
                                               busy_destination=None,
                                               congestion_destination=None,
                                               fail_destination=None))



def test_get_all_parameters():
    with fixtures.user(fallbacks={'noanswer_destination': {'type': 'none'},
                          'busy_destination': {'type': 'none'},
                          'congestion_destination': {'type': 'none'},
                          'fail_destination': {'type': 'none'}}) as user:
        response = confd.users(user['uuid']).fallbacks.get()
        assert_that(response.item, has_entries(noanswer_destination={'type': 'none'},
                                               busy_destination={'type': 'none'},
                                               congestion_destination={'type': 'none'},
                                               fail_destination={'type': 'none'}))



def test_edit():
    with fixtures.user() as user:
        response = confd.users(user['uuid']).fallbacks.put({})
        response.assert_updated()



def test_edit_with_all_parameters():
    with fixtures.user() as user:
        parameters = {'noanswer_destination': {'type': 'none'},
                      'busy_destination': {'type': 'none'},
                      'congestion_destination': {'type': 'none'},
                      'fail_destination': {'type': 'none'}}
        response = confd.users(user['id']).fallbacks.put(parameters)
        response.assert_updated()



def test_edit_to_none():
    with fixtures.user(fallbacks={'noanswer_destination': {'type': 'none'},
                          'busy_destination': {'type': 'none'},
                          'congestion_destination': {'type': 'none'},
                          'fail_destination': {'type': 'none'}}) as user:
        response = confd.users(user['uuid']).fallbacks.put(noanswer_destination=None,
                                                           busy_destination=None,
                                                           congestion_destination=None,
                                                           fail_destination=None)
        response.assert_updated

        response = confd.users(user['uuid']).fallbacks.get()
        assert_that(response.item, has_entries(noanswer_destination=None,
                                               busy_destination=None,
                                               congestion_destination=None,
                                               fail_destination=None))



def test_valid_destinations():
    with fixtures.user() as user, \
            fixtures.meetme() as meetme, \
            fixtures.ivr() as ivr, \
            fixtures.group() as group, \
            fixtures.outcall() as outcall, \
            fixtures.queue() as queue, \
            fixtures.switchboard() as switchboard, \
            fixtures.user() as user2, \
            fixtures.voicemail() as voicemail, \
            fixtures.conference() as conference, \
            fixtures.skill_rule() as skill_rule, \
            fixtures.application() as application:

        destinations = (meetme, ivr, group, outcall, queue, switchboard,
                        user2, voicemail, conference, skill_rule, application)
        for destination in valid_destinations(*destinations):
            _update_user_fallbacks_with_destination(user['uuid'], destination)


def _update_user_fallbacks_with_destination(user_id, destination):
    response = confd.users(user_id).fallbacks.put(noanswer_destination=destination,
                                                  busy_destination=destination,
                                                  congestion_destination=destination,
                                                  fail_destination=destination)
    response.assert_updated()
    response = confd.users(user_id).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=has_entries(**destination),
                                           busy_destination=has_entries(**destination),
                                           congestion_destination=has_entries(**destination),
                                           fail_destination=has_entries(**destination)))


def test_nonexistent_destinations():
    with fixtures.user() as user:
        meetme = ivr = group = outcall = queue = dest_user = voicemail = conference = skill_rule = {'id': 99999999}
        switchboard = application = {'uuid': '00000000-0000-0000-0000-000000000000'}
        for destination in valid_destinations(meetme, ivr, group, outcall, queue, switchboard,
                                              dest_user, voicemail, conference, skill_rule, application):
            if destination['type'] in ('meetme',
                                       'ivr',
                                       'group',
                                       'outcall',
                                       'queue',
                                       'switchboard',
                                       'user',
                                       'voicemail',
                                       'conference'):
                _update_user_fallbacks_with_nonexistent_destination(user['uuid'], destination)

            if destination['type'] == 'application' and destination['application'] == 'custom':
                _update_user_fallbacks_with_nonexistent_destination(user['uuid'], destination)



def _update_user_fallbacks_with_nonexistent_destination(user_id, destination):
    response = confd.users(user_id).fallbacks.put(noanswer_destination=destination,
                                                  busy_destination=destination,
                                                  congestion_destination=destination,
                                                  fail_destination=destination)
    response.assert_status(400)


def test_bus_events():
    with fixtures.user() as user:
        url = confd.users(user['uuid']).fallbacks.put
        s.check_bus_event('config.users.fallbacks.edited', url)



def test_get_fallbacks_relation():
    with fixtures.user(fallbacks={'noanswer_destination': {'type': 'none'},
                          'busy_destination': {'type': 'none'},
                          'congestion_destination': {'type': 'none'},
                          'fail_destination': {'type': 'none'}}) as user:
        response = confd.users(user['uuid']).get()
        assert_that(response.item, has_entries(
            fallbacks=has_entries(noanswer_destination=has_entries(type='none'),
                                  busy_destination=has_entries(type='none'),
                                  congestion_destination=has_entries(type='none'),
                                  fail_destination=has_entries(type='none'))
        ))

