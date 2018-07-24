# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    equal_to,
    has_entries
)
from . import confd
from ..helpers import (
    fixtures,
    scenarios as s,
)
from ..helpers.helpers.destination import invalid_destinations, valid_destinations


FAKE_ID = 999999999


def test_get_errors():
    fake_queue = confd.queues(FAKE_ID).fallbacks.get
    yield s.check_resource_not_found, fake_queue, 'Queue'


@fixtures.queue()
def test_put_errors(queue):
    fake_queue = confd.queues(FAKE_ID).fallbacks.put
    yield s.check_resource_not_found, fake_queue, 'Queue'

    url = confd.queues(queue['id']).fallbacks.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    for destination in invalid_destinations():
        yield s.check_bogus_field_returns_error, url, 'noanswer_destination', destination


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
    assert_that(response.item, has_entries(
        noanswer_destination=None,
        busy_destination=None,
        congestion_destination=None,
        fail_destination=None,
    ))


@fixtures.queue()
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
def test_valid_destinations(queue, meetme, ivr, group, outcall, dest_queue,
                            switchboard, user, voicemail, conference, skill_rule):
    for destination in valid_destinations(meetme, ivr, group, outcall, dest_queue, switchboard,
                                          user, voicemail, conference, skill_rule):
        yield _update_queue_fallbacks_with_destination, queue['id'], destination


def _update_queue_fallbacks_with_destination(queue_id, destination):
    response = confd.queues(queue_id).fallbacks.put(noanswer_destination=destination)
    response.assert_updated()
    response = confd.queues(queue_id).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=has_entries(**destination)))


@fixtures.queue()
def test_nonexistent_destinations(queue):
    meetme = ivr = group = outcall = dest_queue = user = voicemail = conference = skill_rule = {'id': 99999999}
    switchboard = {'uuid': '00000000-0000-0000-0000-000000000000'}
    for destination in valid_destinations(meetme, ivr, group, outcall, dest_queue, switchboard,
                                          user, voicemail, conference, skill_rule):
        if destination['type'] in ('meetme',
                                   'ivr',
                                   'group',
                                   'outcall',
                                   'queue',
                                   'switchboard',
                                   'user',
                                   'voicemail',
                                   'conference'):
            yield _update_user_fallbacks_with_nonexistent_destination, queue['id'], destination


def _update_user_fallbacks_with_nonexistent_destination(queue_id, destination):
    response = confd.queues(queue_id).fallbacks.put(noanswer_destination=destination)
    response.assert_status(400)


@fixtures.queue()
def test_bus_events(queue):
    url = confd.queues(queue['id']).fallbacks.put
    yield s.check_bus_event, 'config.queues.fallbacks.edited', url
