# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, equal_to, has_entries

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from ..helpers.helpers.destination import invalid_destinations, valid_destinations
from . import confd

FAKE_ID = 999999999


def test_get_errors():
    fake_call_filter = confd.callfilters(FAKE_ID).fallbacks.get
    s.check_resource_not_found(fake_call_filter, 'CallFilter')


@fixtures.call_filter()
@fixtures.user()
def test_put_errors(call_filter, user):
    fake_call_filter = confd.callfilters(FAKE_ID).fallbacks.put
    s.check_resource_not_found(fake_call_filter, 'CallFilter')

    url = confd.callfilters(call_filter['id']).fallbacks.put
    error_checks(url, user)


def error_checks(url, user):
    for destination in invalid_destinations():
        s.check_bogus_field_returns_error(url, 'noanswer_destination', destination)
    s.check_bogus_field_returns_error(
        url,
        'noanswer_destination',
        {
            'type': 'user',
            'user_id': user['id'],
            'moh_uuid': '00000000-0000-0000-0000-000000000000',
        },
        {},
        'MOH was not found',
    )


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


@fixtures.call_filter(wazo_tenant=MAIN_TENANT)
@fixtures.call_filter(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.callfilters(main['id']).fallbacks.get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='CallFilter'))

    response = confd.callfilters(sub['id']).fallbacks.get(wazo_tenant=MAIN_TENANT)
    response.assert_ok()


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

    response = confd.callfilters(call_filter['id']).fallbacks.put(
        noanswer_destination=None
    )
    response.assert_updated

    response = confd.callfilters(call_filter['id']).fallbacks.get()
    assert_that(response.item, has_entries(noanswer_destination=None))


@fixtures.call_filter(wazo_tenant=MAIN_TENANT)
@fixtures.call_filter(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.callfilters(main['id']).fallbacks.put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='CallFilter'))

    response = confd.callfilters(sub['id']).fallbacks.put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.call_filter()
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
def test_valid_destinations(call_filter, *destinations):
    for destination in valid_destinations(*destinations):
        _update_call_filter_fallbacks_with_destination(call_filter['id'], destination)


def _update_call_filter_fallbacks_with_destination(call_filter_id, destination):
    response = confd.callfilters(call_filter_id).fallbacks.put(
        noanswer_destination=destination
    )
    response.assert_updated()
    response = confd.callfilters(call_filter_id).fallbacks.get()
    assert_that(
        response.item, has_entries(noanswer_destination=has_entries(**destination))
    )


@fixtures.call_filter()
@fixtures.moh()
def test_nonexistent_destinations(call_filter, moh):
    ivr = group = outcall = queue = user = voicemail = conference = skill_rule = {
        'id': 99999999
    }
    switchboard = application = {'uuid': '00000000-0000-0000-0000-000000000000'}
    for destination in valid_destinations(
        ivr,
        group,
        outcall,
        queue,
        switchboard,
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
        ):
            _update_user_fallbacks_with_nonexistent_destination(
                call_filter['id'], destination
            )

        if (
            destination['type'] == 'application'
            and destination['application'] == 'custom'
        ):
            _update_user_fallbacks_with_nonexistent_destination(
                call_filter['id'], destination
            )


def _update_user_fallbacks_with_nonexistent_destination(call_filter_id, destination):
    response = confd.callfilters(call_filter_id).fallbacks.put(
        noanswer_destination=destination
    )
    response.assert_status(400)


@fixtures.call_filter()
def test_bus_events(call_filter):
    url = confd.callfilters(call_filter['id']).fallbacks.put
    expected_headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event('call_filter_fallback_edited', expected_headers, url)


@fixtures.call_filter()
def test_get_fallbacks_relation(call_filter):
    confd.callfilters(call_filter['id']).fallbacks.put(
        noanswer_destination={'type': 'none'}
    ).assert_updated
    response = confd.callfilters(call_filter['id']).get()
    assert_that(
        response.item,
        has_entries(
            fallbacks=has_entries(noanswer_destination=has_entries(type='none'))
        ),
    )
