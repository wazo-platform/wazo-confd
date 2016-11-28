# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
# Copyright (C) 2016 Francois Blackburn
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

from hamcrest import (assert_that,
                      equal_to,
                      has_entries)
from test_api import scenarios as s
from test_api import confd
from test_api import fixtures
from test_api.helpers.destination import invalid_destinations, valid_destinations


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
@fixtures.user()
@fixtures.voicemail()
def test_valid_destinations(group, conference, ivr, dest_group, outcall, queue, user, voicemail):
    for destination in valid_destinations(conference, ivr, dest_group, outcall, queue, user, voicemail):
        yield _update_group_fallbacks_with_destination, group['id'], destination


def _update_group_fallbacks_with_destination(group_id, destination):
    response = confd.groups(group_id).fallbacks.put(noanswer_destination=destination)
    response.assert_updated()
    response = confd.groups(group_id).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=has_entries(**destination)))


@fixtures.group()
def test_bus_events(group):
    url = confd.groups(group['id']).fallbacks.put
    yield s.check_bus_event, 'config.groups.fallbacks.edited', url


@fixtures.group()
def test_get_fallbacks_relation(group):
    confd.groups(group['id']).fallbacks.put(noanswer_destination={'type': 'none'}).assert_updated
    response = confd.groups(group['id']).get()
    assert_that(response.item, has_entries(
        fallbacks=has_entries(noanswer_destination=has_entries(type='none'))
    ))
