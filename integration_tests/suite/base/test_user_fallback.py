# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from hamcrest import assert_that, has_entries
from test_api import scenarios as s
from test_api import confd
from test_api import fixtures
from test_api.helpers.destination import invalid_destinations, valid_destinations


FAKE_ID = 999999999


def test_get_errors():
    fake_user = confd.users(FAKE_ID).fallbacks.get
    yield s.check_resource_not_found, fake_user, 'User'


@fixtures.user()
def test_put_errors(user):
    fake_user = confd.users(FAKE_ID).fallbacks.put
    yield s.check_resource_not_found, fake_user, 'User'

    url = confd.users(user['uuid']).fallbacks.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    for destination in invalid_destinations():
        yield s.check_bogus_field_returns_error, url, 'noanswer_destination', destination
        yield s.check_bogus_field_returns_error, url, 'busy_destination', destination
        yield s.check_bogus_field_returns_error, url, 'congestion_destination', destination
        yield s.check_bogus_field_returns_error, url, 'fail_destination', destination


@fixtures.user()
def test_get(user):
    response = confd.users(user['uuid']).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=None,
                                           busy_destination=None,
                                           congestion_destination=None,
                                           fail_destination=None))


@fixtures.user()
def test_get_all_parameters(user):
    parameters = {'noanswer_destination': {'type': 'none'},
                  'busy_destination': {'type': 'none'},
                  'congestion_destination': {'type': 'none'},
                  'fail_destination': {'type': 'none'}}
    confd.users(user['id']).fallbacks.put(parameters).assert_updated()
    response = confd.users(user['uuid']).fallbacks.get()
    assert_that(response.item, has_entries(**parameters))


@fixtures.user()
def test_edit(user):
    response = confd.users(user['uuid']).fallbacks.put({})
    response.assert_updated()


@fixtures.user()
def test_edit_with_all_parameters(user):
    parameters = {'noanswer_destination': {'type': 'none'},
                  'busy_destination': {'type': 'none'},
                  'congestion_destination': {'type': 'none'},
                  'fail_destination': {'type': 'none'}}
    response = confd.users(user['id']).fallbacks.put(parameters)
    response.assert_updated()


@fixtures.user()
def test_edit_to_none(user):
    parameters = {'noanswer_destination': {'type': 'none'},
                  'busy_destination': {'type': 'none'},
                  'congestion_destination': {'type': 'none'},
                  'fail_destination': {'type': 'none'}}
    confd.users(user['uuid']).fallbacks.put(parameters).assert_updated()

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


@fixtures.user()
@fixtures.meetme()
@fixtures.ivr()
@fixtures.group()
@fixtures.outcall()
@fixtures.queue()
@fixtures.switchboard()
@fixtures.user()
@fixtures.voicemail()
@fixtures.conference()
def test_valid_destinations(user, meetme, ivr, group, outcall, queue, switchboard, dest_user, voicemail, conference):
    for destination in valid_destinations(meetme, ivr, group, outcall, queue, switchboard, dest_user, voicemail, conference):
        yield _update_user_fallbacks_with_destination, user['uuid'], destination


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


@fixtures.user()
def test_nonexistent_destinations(user):
    meetme = ivr = group = outcall = queue = dest_user = voicemail = conference = {'id': 99999999}
    switchboard = {'uuid': '00000000-0000-0000-0000-000000000000'}
    for destination in valid_destinations(meetme, ivr, group, outcall, queue, switchboard, dest_user, voicemail, conference):
        if destination['type'] in ('meetme',
                                   'ivr',
                                   'group',
                                   'outcall',
                                   'queue',
                                   'switchboard',
                                   'user',
                                   'voicemail',
                                   'conference'):
            yield _update_user_fallbacks_with_nonexistent_destination, user['uuid'], destination


def _update_user_fallbacks_with_nonexistent_destination(user_id, destination):
    response = confd.users(user_id).fallbacks.put(noanswer_destination=destination,
                                                  busy_destination=destination,
                                                  congestion_destination=destination,
                                                  fail_destination=destination)
    response.assert_status(400)


@fixtures.user()
def test_bus_events(user):
    url = confd.users(user['uuid']).fallbacks.put
    yield s.check_bus_event, 'config.users.fallbacks.edited', url


@fixtures.user()
def test_get_fallbacks_relation(user):
    confd.users(user['uuid']).fallbacks.put(noanswer_destination={'type': 'none'},
                                            busy_destination={'type': 'none'},
                                            congestion_destination={'type': 'none'},
                                            fail_destination={'type': 'none'}).assert_updated
    response = confd.users(user['uuid']).get()
    assert_that(response.item, has_entries(
        fallbacks=has_entries(noanswer_destination=has_entries(type='none'),
                              busy_destination=has_entries(type='none'),
                              congestion_destination=has_entries(type='none'),
                              fail_destination=has_entries(type='none'))
    ))
