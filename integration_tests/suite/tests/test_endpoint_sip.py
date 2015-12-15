# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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


from test_api import confd
from test_api import fixtures
from test_api import scenarios as s
from test_api import errors as e

from hamcrest import assert_that, has_entries, has_length, has_items, \
    instance_of, contains, has_entry

ALL_OPTIONS = [
    ['buggymwi', '1'],
    ['amaflags', 'default'],
    ['sendrpid', 'yes'],
    ['videosupport', 'yes'],
    ['maxcallbitrate', '1024'],
    ['registertrying', '1'],
    ['session-minse', '10'],
    ['maxforwards', '1'],
    ['rtpholdtimeout', '15'],
    ['session-expires', '60'],
    ['ignoresdpversion', '1'],
    ['textsupport', '1'],
    ['unsolicited_mailbox', '1000@default'],
    ['fromuser', 'field-user'],
    ['useclientcode', '1'],
    ['call-limit', '1'],
    ['progressinband', 'yes'],
    ['transport', 'udp'],
    ['directmedia', 'update'],
    ['promiscredir', '1'],
    ['allowoverlap', '1'],
    ['dtmfmode', 'info'],
    ['language', 'fr_FR'],
    ['usereqphone', '1'],
    ['qualify', '500'],
    ['trustrpid', '1'],
    ['timert1', '1'],
    ['session-refresher', 'uas'],
    ['allowsubscribe', '1'],
    ['session-timers', 'originate'],
    ['busylevel', '1'],
    ['callcounter', '0'],
    ['callerid', '"customcallerid" <1234>'],
    ['encryption', '1'],
    ['use_q850_reason', '1'],
    ['disallowed_methods', 'disallowsip'],
    ['rfc2833compensate', '1'],
    ['g726nonstandard', '1'],
    ['contactdeny', '127.0.0.1'],
    ['snom_aoc_enabled', '1'],
    ['t38pt_udptl', '1'],
    ['subscribemwi', 'no'],
    ['autoframing', '1'],
    ['t38pt_usertpsource', '1'],
    ['fromdomain', 'field-domain'],
    ['allowtransfer', '1'],
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
    ['allow', 'gsm'],
    ['setvar', 'setvar'],
    ['accountcode', 'accountcode'],
    ['md5secret', 'abcdefg'],
    ['mohinterpret', 'mohinterpret'],
    ['vmexten', '1000'],
    ['callingpres', '1'],
    ['parkinglot', '700'],
    ['fullcontact', 'fullcontact'],
    ['fullname', 'fullname'],
    ['defaultip', '127.0.0.1'],
    ['qualifyfreq', '5000'],
    ['protocol', 'sip'],
    ['regexten', 'regexten'],
    ['regseconds', '60'],
    ['regserver', '127.0.0.1'],
    ['ipaddr', '127.0.0.1'],
    ['lastms', '500'],
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


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'username', 123
    yield s.check_bogus_field_returns_error, url, 'username', ']^',
    yield s.check_bogus_field_returns_error, url, 'secret', 123
    yield s.check_bogus_field_returns_error, url, 'secret', ']^',
    yield s.check_bogus_field_returns_error, url, 'type', 123
    yield s.check_bogus_field_returns_error, url, 'options', [['bogus', 'bogus']]
    yield s.check_bogus_field_returns_error, url, 'username', 'ûsername'
    yield s.check_bogus_field_returns_error, url, 'secret', 'pâssword'


@fixtures.sip()
def test_delete_errors(sip):
    url = confd.endpoints.sip(sip['id'])
    url.delete()
    yield s.check_resource_not_found, url.get, 'SIPEndpoint'


@fixtures.sip()
def test_get(sip):
    expected = has_entries({'username': has_length(8),
                            'secret': has_length(8),
                            'type': 'friend',
                            'host': 'dynamic',
                            'options': instance_of(list),
                            })

    response = confd.endpoints.sip(sip['id']).get()
    assert_that(response.item, expected)


@fixtures.sip()
@fixtures.sip()
def test_list(sip1, sip2):
    expected = has_items(has_entry('id', sip1['id']),
                         has_entry('id', sip2['id']))

    response = confd.endpoints.sip.get()
    assert_that(response.items, expected)

    expected = contains(has_entry('id', sip1['id']))

    response = confd.endpoints.sip.get(search=sip1['username'])
    assert_that(response.items, expected)


def test_create_sip_with_minimal_parameters():
    expected = has_entries({'username': has_length(8),
                            'secret': has_length(8),
                            'type': 'friend',
                            'host': 'dynamic',
                            'options': instance_of(list),
                            })

    response = confd.endpoints.sip.post()

    response.assert_created('endpoint_sip', location='endpoints/sip')
    assert_that(response.item, expected)


def test_create_sip_with_all_parameters():
    expected = has_entries({'username': 'myusername',
                            'secret': 'mysecret',
                            'type': 'peer',
                            'host': '127.0.0.1',
                            'options': has_items(*ALL_OPTIONS)
                            })

    response = confd.endpoints.sip.post(username="myusername",
                                        secret="mysecret",
                                        type="peer",
                                        host="127.0.0.1",
                                        options=ALL_OPTIONS)

    assert_that(response.item, expected)


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
    assert_that(response.item, has_entries({'username': 'updatedusername',
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


@fixtures.sip()
def test_delete_sip(sip):
    response = confd.endpoints.sip(sip['id']).delete()
    response.assert_deleted()
