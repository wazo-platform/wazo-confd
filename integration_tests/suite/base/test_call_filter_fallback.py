# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
)
from . import confd
from ..helpers import (
    errors as e,
    scenarios as s,
    fixtures,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)
from ..helpers.helpers.destination import invalid_destinations, valid_destinations


FAKE_ID = 999999999


def test_get_errors():
    fake_call_filter = confd.callfilters(FAKE_ID).fallbacks.get
    s.check_resource_not_found(fake_call_filter, 'CallFilter')


def test_put_errors():
    with fixtures.call_filter() as call_filter:
        fake_call_filter = confd.callfilters(FAKE_ID).fallbacks.put
        s.check_resource_not_found(fake_call_filter, 'CallFilter')

        url = confd.callfilters(call_filter['id']).fallbacks.put
        error_checks(url)



def error_checks(url):
    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'noanswer_destination', destination)


def test_get():
    with fixtures.call_filter() as call_filter:
        response = confd.callfilters(call_filter['id']).fallbacks.get()
        assert_that(response.item, has_entries(noanswer_destination=None))



def test_get_all_parameters():
    with fixtures.call_filter() as call_filter:
        parameters = {'noanswer_destination': {'type': 'none'}}
        confd.callfilters(call_filter['id']).fallbacks.put(parameters).assert_updated()
        response = confd.callfilters(call_filter['id']).fallbacks.get()
        assert_that(response.item, equal_to(parameters))



def test_get_multi_tenant():
    with fixtures.call_filter(wazo_tenant=MAIN_TENANT) as main, fixtures.call_filter(wazo_tenant=SUB_TENANT) as sub:
        response = confd.callfilters(main['id']).fallbacks.get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='CallFilter'))

        response = confd.callfilters(sub['id']).fallbacks.get(wazo_tenant=MAIN_TENANT)
        response.assert_ok()



def test_edit():
    with fixtures.call_filter() as call_filter:
        response = confd.callfilters(call_filter['id']).fallbacks.put({})
        response.assert_updated()



def test_edit_with_all_parameters():
    with fixtures.call_filter() as call_filter:
        parameters = {'noanswer_destination': {'type': 'none'}}
        response = confd.callfilters(call_filter['id']).fallbacks.put(parameters)
        response.assert_updated()



def test_edit_to_none():
    with fixtures.call_filter() as call_filter:
        parameters = {'noanswer_destination': {'type': 'none'}}
        confd.callfilters(call_filter['id']).fallbacks.put(parameters).assert_updated()

        response = confd.callfilters(call_filter['id']).fallbacks.put(noanswer_destination=None)
        response.assert_updated

        response = confd.callfilters(call_filter['id']).fallbacks.get()
        assert_that(response.item, has_entries(noanswer_destination=None))



def test_edit_multi_tenant():
    with fixtures.call_filter(wazo_tenant=MAIN_TENANT) as main, fixtures.call_filter(wazo_tenant=SUB_TENANT) as sub:
        response = confd.callfilters(main['id']).fallbacks.put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='CallFilter'))

        response = confd.callfilters(sub['id']).fallbacks.put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()



def test_valid_destinations():
    with fixtures.call_filter() as call_filter, \
            fixtures.meetme() as meetme, \
            fixtures.ivr() as ivr, \
            fixtures.group() as group, \
            fixtures.outcall() as outcall, \
            fixtures.queue() as queue, \
            fixtures.switchboard() as switchboard, \
            fixtures.user() as user, \
            fixtures.voicemail() as voicemail, \
            fixtures.conference() as conference, \
            fixtures.skill_rule() as skill_rule, \
            fixtures.application() as application:

        destinations = (meetme, ivr, group, outcall, queue, switchboard, user,
                        voicemail, conference, skill_rule, application)
        for destination in valid_destinations(*destinations):
            _update_call_filter_fallbacks_with_destination(call_filter['id'], destination)


def _update_call_filter_fallbacks_with_destination(call_filter_id, destination):
    response = confd.callfilters(call_filter_id).fallbacks.put(noanswer_destination=destination)
    response.assert_updated()
    response = confd.callfilters(call_filter_id).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=has_entries(**destination)))


def test_nonexistent_destinations():
    with fixtures.call_filter() as call_filter:
        meetme = ivr = group = outcall = queue = user = voicemail = conference = skill_rule = {'id': 99999999}
        switchboard = application = {'uuid': '00000000-0000-0000-0000-000000000000'}
        for destination in valid_destinations(meetme, ivr, group, outcall, queue, switchboard, user,
                                              voicemail, conference, skill_rule, application):
            if destination['type'] in ('meetme',
                                       'ivr',
                                       'group',
                                       'outcall',
                                       'queue',
                                       'switchboard',
                                       'user',
                                       'voicemail',
                                       'conference'):
                _update_user_fallbacks_with_nonexistent_destination(call_filter['id'], destination)

            if destination['type'] == 'application' and destination['application'] == 'custom':
                _update_user_fallbacks_with_nonexistent_destination(call_filter['id'], destination)



def _update_user_fallbacks_with_nonexistent_destination(call_filter_id, destination):
    response = confd.callfilters(call_filter_id).fallbacks.put(noanswer_destination=destination)
    response.assert_status(400)


def test_bus_events():
    with fixtures.call_filter() as call_filter:
        url = confd.callfilters(call_filter['id']).fallbacks.put
        s.check_bus_event('config.callfilters.fallbacks.edited', url)



def test_get_fallbacks_relation():
    with fixtures.call_filter() as call_filter:
        confd.callfilters(call_filter['id']).fallbacks.put(noanswer_destination={'type': 'none'}).assert_updated
        response = confd.callfilters(call_filter['id']).get()
        assert_that(response.item, has_entries(
            fallbacks=has_entries(noanswer_destination=has_entries(type='none'))
        ))

