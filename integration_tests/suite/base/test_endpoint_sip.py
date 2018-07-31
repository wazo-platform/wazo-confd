# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    all_of,
    assert_that,
    contains,
    has_entries,
    has_entry,
    has_items,
    has_length,
    instance_of,
    not_,
)

from . import confd
from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)

ALL_OPTIONS = [
    ['buggymwi', 'yes'],
    ['amaflags', 'default'],
    ['sendrpid', 'yes'],
    ['videosupport', 'yes'],
    ['maxcallbitrate', '1024'],
    ['session-minse', '10'],
    ['maxforwards', '1'],
    ['rtpholdtimeout', '15'],
    ['session-expires', '60'],
    ['ignoresdpversion', 'yes'],
    ['textsupport', 'yes'],
    ['unsolicited_mailbox', '1000@default'],
    ['fromuser', 'field-user'],
    ['useclientcode', 'yes'],
    ['call-limit', '1'],
    ['progressinband', 'yes'],
    ['transport', 'udp'],
    ['directmedia', 'update'],
    ['promiscredir', 'yes'],
    ['allowoverlap', 'yes'],
    ['dtmfmode', 'info'],
    ['language', 'fr_FR'],
    ['usereqphone', 'yes'],
    ['qualify', '500'],
    ['trustrpid', 'yes'],
    ['timert1', '1'],
    ['session-refresher', 'uas'],
    ['allowsubscribe', 'yes'],
    ['session-timers', 'originate'],
    ['busylevel', '1'],
    ['callcounter', 'no'],
    ['callerid', '"customcallerid" <1234>'],
    ['encryption', 'yes'],
    ['use_q850_reason', 'yes'],
    ['disallowed_methods', 'disallowsip'],
    ['rfc2833compensate', 'yes'],
    ['g726nonstandard', 'yes'],
    ['contactdeny', '127.0.0.1'],
    ['snom_aoc_enabled', 'yes'],
    ['t38pt_udptl', 'yes'],
    ['subscribemwi', 'no'],
    ['autoframing', 'yes'],
    ['t38pt_usertpsource', 'yes'],
    ['fromdomain', 'field-domain'],
    ['allowtransfer', 'yes'],
    ['nat', 'force_rport,comedia'],
    ['contactpermit', '127.0.0.1'],
    ['rtpkeepalive', '15'],
    ['insecure', 'port'],
    ['permit', '127.0.0.1'],
    ['deny', '127.0.0.1'],
    ['timerb', '1'],
    ['rtptimeout', '15'],
    ['disallow', 'all'],
    ['allow', 'g723'],
    ['accountcode', 'accountcode'],
    ['md5secret', 'abcdefg'],
    ['mohinterpret', 'mohinterpret'],
    ['vmexten', '1000'],
    ['callingpres', '1'],
    ['parkinglot', '700'],
    ['fullname', 'fullname'],
    ['defaultip', '127.0.0.1'],
    ['qualifyfreq', '5000'],
    ['regexten', 'regexten'],
    ['cid_number', '0123456789'],
    ['callbackextension', '0123456789'],
    ['port', '10000'],
    ['outboundproxy', '127.0.0.1'],
    ['remotesecret', 'remotesecret'],
]


def test_get_errors():
    fake_sip_get = confd.endpoints.sip(999999).get
    yield s.check_resource_not_found, fake_sip_get, 'SIPEndpoint'


def test_post_errors():
    url = confd.endpoints.sip.post
    for check in error_checks(url):
        yield check


@fixtures.sip()
def test_put_errors(sip):
    url = confd.endpoints.sip(sip['id']).put
    for check in error_checks(url):
        yield check

    yield s.check_bogus_field_returns_error, url, 'username', None
    yield s.check_bogus_field_returns_error, url, 'secret', None
    yield s.check_bogus_field_returns_error, url, 'type', None
    yield s.check_bogus_field_returns_error, url, 'host', None
    yield s.check_bogus_field_returns_error, url, 'options', None


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'username', 123
    yield s.check_bogus_field_returns_error, url, 'username', ']^',
    yield s.check_bogus_field_returns_error, url, 'username', 'ûsername'
    yield s.check_bogus_field_returns_error, url, 'username', [],
    yield s.check_bogus_field_returns_error, url, 'username', {},
    yield s.check_bogus_field_returns_error, url, 'secret', 'pâssword'
    yield s.check_bogus_field_returns_error, url, 'secret', 123
    yield s.check_bogus_field_returns_error, url, 'secret', True
    yield s.check_bogus_field_returns_error, url, 'secret', []
    yield s.check_bogus_field_returns_error, url, 'secret', {}
    yield s.check_bogus_field_returns_error, url, 'type', 123
    yield s.check_bogus_field_returns_error, url, 'type', 'invalid_choice'
    yield s.check_bogus_field_returns_error, url, 'type', True
    yield s.check_bogus_field_returns_error, url, 'type', []
    yield s.check_bogus_field_returns_error, url, 'type', {}
    yield s.check_bogus_field_returns_error, url, 'host', 123
    yield s.check_bogus_field_returns_error, url, 'host', True
    yield s.check_bogus_field_returns_error, url, 'host', []
    yield s.check_bogus_field_returns_error, url, 'host', {}
    yield s.check_bogus_field_returns_error, url, 'options', 123
    yield s.check_bogus_field_returns_error, url, 'options', None
    yield s.check_bogus_field_returns_error, url, 'options', {}
    yield s.check_bogus_field_returns_error, url, 'options', 'string'
    yield s.check_bogus_field_returns_error, url, 'options', [None]
    yield s.check_bogus_field_returns_error, url, 'options', ['string', 'string']
    yield s.check_bogus_field_returns_error, url, 'options', [123, 123]
    yield s.check_bogus_field_returns_error, url, 'options', ['string', 123]
    yield s.check_bogus_field_returns_error, url, 'options', [[]]
    yield s.check_bogus_field_returns_error, url, 'options', [{'key': 'value'}]
    yield s.check_bogus_field_returns_error, url, 'options', [['missing_value']]
    yield s.check_bogus_field_returns_error, url, 'options', [['too', 'much', 'value']]
    yield s.check_bogus_field_returns_error, url, 'options', [['wrong_value', 1234]]
    yield s.check_bogus_field_returns_error, url, 'options', [['none_value', None]]


@fixtures.sip()
def test_delete_errors(sip):
    url = confd.endpoints.sip(sip['id'])
    url.delete()
    yield s.check_resource_not_found, url.get, 'SIPEndpoint'


@fixtures.sip(wazo_tenant=MAIN_TENANT)
@fixtures.sip(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.endpoints.sip.get(wazo_tenant=MAIN_TENANT)
    assert_that(
        response.items,
        all_of(has_items(main)), not_(has_items(sub)),
    )

    response = confd.endpoints.sip.get(wazo_tenant=SUB_TENANT)
    assert_that(
        response.items,
        all_of(has_items(sub), not_(has_items(main))),
    )

    response = confd.endpoints.sip.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(
        response.items,
        has_items(main, sub),
    )


@fixtures.sip()
def test_get(sip):
    response = confd.endpoints.sip(sip['id']).get()
    assert_that(response.item, has_entries({
        'username': has_length(8),
        'secret': has_length(8),
        'type': 'friend',
        'host': 'dynamic',
        'options': instance_of(list),
        'trunk': None,
        'line': None,
    }))


@fixtures.sip()
@fixtures.sip()
def test_list(sip1, sip2):
    response = confd.endpoints.sip.get()
    assert_that(response.items, has_items(
        has_entry('id', sip1['id']),
        has_entry('id', sip2['id']),
    ))

    response = confd.endpoints.sip.get(search=sip1['username'])
    assert_that(response.items, contains(has_entry('id', sip1['id'])))


def test_create_sip_with_minimal_parameters():
    response = confd.endpoints.sip.post()

    response.assert_created('endpoint_sip', location='endpoints/sip')
    assert_that(response.item,  has_entries({
        'username': has_length(8),
        'secret': has_length(8),
        'type': 'friend',
        'host': 'dynamic',
        'options': instance_of(list),
    }))


def test_create_sip_with_all_parameters():
    response = confd.endpoints.sip.post(username="myusername",
                                        secret="mysecret",
                                        type="peer",
                                        host="127.0.0.1",
                                        options=ALL_OPTIONS)

    assert_that(response.item, has_entries({
        'username': 'myusername',
        'secret': 'mysecret',
        'type': 'peer',
        'host': '127.0.0.1',
        'options': has_items(*ALL_OPTIONS)
    }))


def test_create_sip_with_additional_options():
    options = ALL_OPTIONS + [
        ["foo", "bar"],
        ["spam", "eggs"]
    ]

    response = confd.endpoints.sip.post(options=options)
    assert_that(response.item['options'], has_items(*options))


@fixtures.sip(username="dupusername")
def test_create_sip_with_username_already_taken(sip):
    response = confd.endpoints.sip.post(username="dupusername")
    response.assert_match(400, e.resource_exists('SIPEndpoint'))


@fixtures.sip()
def test_update_required_parameters(sip):
    url = confd.endpoints.sip(sip['id'])

    response = url.put(username="updatedusername",
                       secret="updatedsecret",
                       type="peer",
                       host="127.0.0.1")
    response.assert_updated()

    response = url.get()
    assert_that(response.item, has_entries({
        'username': 'updatedusername',
        'secret': 'updatedsecret',
        'type': 'peer',
        'host': '127.0.0.1',
    }))


@fixtures.sip(options=[["allow", "gsm"], ["nat", "force_rport,comedia"]])
def test_update_options(sip):
    options = [
        ["allow", "g723"],
        ["insecure", "port"]
    ]

    url = confd.endpoints.sip(sip['id'])
    response = url.put(options=options)
    response.assert_updated()

    response = url.get()
    assert_that(response.item['options'], has_items(*options))


@fixtures.sip(options=[
    ["allow", "gsm"],
    ["foo", "bar"],
    ["foo", "baz"],
    ["spam", "eggs"]
])
def test_update_additional_options(sip):
    options = [
        ["allow", "g723"],
        ["foo", "newbar"],
        ["foo", "newbaz"],
        ["spam", "neweggs"]
    ]

    url = confd.endpoints.sip(sip['id'])
    response = url.put(options=options)
    response.assert_updated()

    response = url.get()
    assert_that(response.item['options'], has_items(*options))


@fixtures.sip(host="static")
def test_update_values_other_than_host_does_not_touch_it(sip):
    response = confd.endpoints.sip(sip['id']).put(username="testhost")
    response.assert_ok()

    response = confd.endpoints.sip(sip['id']).get()
    assert_that(response.item, has_entries(host="static"))


@fixtures.sip()
def test_delete_sip(sip):
    response = confd.endpoints.sip(sip['id']).delete()
    response.assert_deleted()
