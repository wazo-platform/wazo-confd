# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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
    s.check_resource_not_found(fake_queue, 'Queue')


def test_put_errors():
    with fixtures.queue() as queue:
        fake_queue = confd.queues(FAKE_ID).fallbacks.put
        s.check_resource_not_found(fake_queue, 'Queue')

        url = confd.queues(queue['id']).fallbacks.put
        error_checks(url)



def error_checks(url):
    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'noanswer_destination', destination)


def test_get():
    with fixtures.queue() as queue:
        response = confd.queues(queue['id']).fallbacks.get()
        assert_that(response.item, has_entries(noanswer_destination=None))



def test_get_all_parameters():
    with fixtures.queue() as queue:
        parameters = {
            'noanswer_destination': {'type': 'none'},
            'busy_destination': {'type': 'none'},
            'congestion_destination': {'type': 'none'},
            'fail_destination': {'type': 'none'},
        }
        confd.queues(queue['id']).fallbacks.put(parameters).assert_updated()
        response = confd.queues(queue['id']).fallbacks.get()
        assert_that(response.item, equal_to(parameters))



def test_edit():
    with fixtures.queue() as queue:
        response = confd.queues(queue['id']).fallbacks.put({})
        response.assert_updated()



def test_edit_with_all_parameters():
    with fixtures.queue() as queue:
        parameters = {
            'noanswer_destination': {'type': 'none'},
            'busy_destination': {'type': 'none'},
            'congestion_destination': {'type': 'none'},
            'fail_destination': {'type': 'none'},
        }
        response = confd.queues(queue['id']).fallbacks.put(parameters)
        response.assert_updated()



def test_edit_to_none():
    with fixtures.queue() as queue:
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



def test_valid_destinations():
    with fixtures.queue() as queue, \
            fixtures.meetme() as meetme, \
            fixtures.ivr() as ivr, \
            fixtures.group() as group, \
            fixtures.outcall() as outcall, \
            fixtures.queue() as queue2, \
            fixtures.switchboard() as switchboard, \
            fixtures.user() as user, \
            fixtures.voicemail() as voicemail, \
            fixtures.conference() as conference, \
            fixtures.skill_rule() as skill_rule, \
            fixtures.application() as application:
        destinations = (meetme, ivr, group, outcall, queue2, switchboard, user,
                        voicemail, conference, skill_rule, application)

        for destination in valid_destinations(*destinations):
            _update_queue_fallbacks_with_destination(queue['id'], destination)


def _update_queue_fallbacks_with_destination(queue_id, destination):
    response = confd.queues(queue_id).fallbacks.put(noanswer_destination=destination)
    response.assert_updated()
    response = confd.queues(queue_id).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=has_entries(**destination)))


def test_nonexistent_destinations():
    with fixtures.queue() as queue:
        meetme = ivr = group = outcall = dest_queue = user = voicemail = conference = skill_rule = {'id': 99999999}
        switchboard = application = {'uuid': '00000000-0000-0000-0000-000000000000'}
        for destination in valid_destinations(meetme, ivr, group, outcall, dest_queue, switchboard,
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
                _update_user_fallbacks_with_nonexistent_destination(queue['id'], destination)

            if destination['type'] == 'application' and destination['application'] == 'custom':
                _update_user_fallbacks_with_nonexistent_destination(queue['id'], destination)



def _update_user_fallbacks_with_nonexistent_destination(queue_id, destination):
    response = confd.queues(queue_id).fallbacks.put(noanswer_destination=destination)
    response.assert_status(400)


def test_bus_events():
    with fixtures.queue() as queue:
        url = confd.queues(queue['id']).fallbacks.put
        s.check_bus_event('config.queues.fallbacks.edited', url)

