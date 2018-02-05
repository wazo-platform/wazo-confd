# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
)
from . import confd
from ..helpers import (
    scenarios as s,
    fixtures,
)
from ..helpers.helpers.destination import invalid_destinations, valid_destinations


FAKE_ID = 999999999


def test_get_errors():
    fake_call_filter = confd.callfilters(FAKE_ID).fallbacks.get
    yield s.check_resource_not_found, fake_call_filter, 'CallFilter'


@fixtures.call_filter()
def test_put_errors(call_filter):
    fake_call_filter = confd.callfilters(FAKE_ID).fallbacks.put
    yield s.check_resource_not_found, fake_call_filter, 'CallFilter'

    url = confd.callfilters(call_filter['id']).fallbacks.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    for destination in invalid_destinations():
        yield s.check_bogus_field_returns_error, url, 'noanswer_destination', destination


@fixtures.call_filter()
def test_get(call_filter):
    response = confd.callfilters(call_filter['id']).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=None))


@fixtures.call_filter()
def test_get_all_parameters(call_filter):
    parameters = {'noanswer_destination': {'type': 'none'}}
    confd.callfilters(call_filter['id']).fallbacks.put(parameters).assert_updated()
    response = confd.callfilters(call_filter['id']).fallbacks.get()
    assert_that(response.item, equal_to(parameters))


@fixtures.call_filter()
def test_edit(call_filter):
    response = confd.callfilters(call_filter['id']).fallbacks.put({})
    response.assert_updated()


@fixtures.call_filter()
def test_edit_with_all_parameters(call_filter):
    parameters = {'noanswer_destination': {'type': 'none'}}
    response = confd.callfilters(call_filter['id']).fallbacks.put(parameters)
    response.assert_updated()


@fixtures.call_filter()
def test_edit_to_none(call_filter):
    parameters = {'noanswer_destination': {'type': 'none'}}
    confd.callfilters(call_filter['id']).fallbacks.put(parameters).assert_updated()

    response = confd.callfilters(call_filter['id']).fallbacks.put(noanswer_destination=None)
    response.assert_updated

    response = confd.callfilters(call_filter['id']).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=None))


@fixtures.call_filter()
@fixtures.meetme()
@fixtures.ivr()
@fixtures.group()
@fixtures.outcall()
@fixtures.queue()
@fixtures.switchboard()
@fixtures.user()
@fixtures.voicemail()
@fixtures.conference()
def test_valid_destinations(call_filter, meetme, ivr, group, outcall, queue, switchboard, user, voicemail, conference):
    for destination in valid_destinations(meetme, ivr, group, outcall, queue, switchboard, user, voicemail, conference):
        yield _update_call_filter_fallbacks_with_destination, call_filter['id'], destination


def _update_call_filter_fallbacks_with_destination(call_filter_id, destination):
    response = confd.callfilters(call_filter_id).fallbacks.put(noanswer_destination=destination)
    response.assert_updated()
    response = confd.callfilters(call_filter_id).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=has_entries(**destination)))


@fixtures.call_filter()
def test_nonexistent_destinations(call_filter):
    meetme = ivr = group = outcall = queue = user = voicemail = conference = {'id': 99999999}
    switchboard = {'uuid': '00000000-0000-0000-0000-000000000000'}
    for destination in valid_destinations(meetme, ivr, group, outcall, queue, switchboard, user, voicemail, conference):
        if destination['type'] in ('meetme',
                                   'ivr',
                                   'group',
                                   'outcall',
                                   'queue',
                                   'switchboard',
                                   'user',
                                   'voicemail',
                                   'conference'):
            yield _update_user_fallbacks_with_nonexistent_destination, call_filter['id'], destination


def _update_user_fallbacks_with_nonexistent_destination(call_filter_id, destination):
    response = confd.callfilters(call_filter_id).fallbacks.put(noanswer_destination=destination)
    response.assert_status(400)


@fixtures.call_filter()
def test_bus_events(call_filter):
    url = confd.callfilters(call_filter['id']).fallbacks.put
    yield s.check_bus_event, 'config.callfilters.fallbacks.edited', url
