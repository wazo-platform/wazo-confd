# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from test_api import scenarios as s
from test_api import confd
from test_api.bus import BusClient

from xivo_test_helpers import until

from hamcrest import assert_that, has_entries, has_length


def test_put_errors():
    url = confd.asterisk.sip.general.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'ordered_options', 123
    yield s.check_bogus_field_returns_error, url, 'ordered_options', None
    yield s.check_bogus_field_returns_error, url, 'ordered_options', {}
    yield s.check_bogus_field_returns_error, url, 'ordered_options', 'string'
    yield s.check_bogus_field_returns_error, url, 'ordered_options', ['string', 'string']
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [123, 123]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', ['string', 123]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [[]]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [{'key': 'value'}]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [['missing_value']]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [['too', 'much', 'value']]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [['wrong_value', 1234]]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [['none_value', None]]

    yield s.check_bogus_field_returns_error, url, 'options', 123
    yield s.check_bogus_field_returns_error, url, 'options', None
    yield s.check_bogus_field_returns_error, url, 'options', 'string'
    yield s.check_bogus_field_returns_error, url, 'options', [['ordered', 'option']]
    yield s.check_bogus_field_returns_error, url, 'options', {'wrong_value': 23}
    yield s.check_bogus_field_returns_error, url, 'options', {'none_value': None}

    yield s.check_bogus_field_returns_error, url, 'options', {'register': 'value'}
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [['register', 'value']]


def test_get():
    response = confd.asterisk.sip.general.get()
    response.assert_ok()


def test_edit_sip_general():
    parameters = {'ordered_options': [['bindport', '5060'],
                                      ['allow', '127.0.0.1'],
                                      ['deny', '192.168.0.0'],
                                      ['allow', '192.168.0.1']],
                  'options': {'nat': 'toto',
                              'username': 'Bob'}}

    response = confd.asterisk.sip.general.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.sip.general.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_sip_general_with_no_option():
    parameters = {'ordered_options': [],
                  'options': {}}
    response = confd.asterisk.sip.general.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.sip.general.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_sip_general_with_none_value():
    parameters = {'ordered_options': [['bindport', 'ip']],
                  'options': {'nat': 'value'}}

    response = confd.asterisk.sip.general.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.sip.general.get()
    assert_that(response.item, has_entries(parameters))


def test_bus_event_when_edited():
    BusClient.listen_events('config.sip_general.edited')
    confd.asterisk.sip.general.put({'ordered_options': [],
                                    'options': {}}).assert_updated()

    def assert_function():
        assert_that(BusClient.events(), has_length(1))

    until.assert_(assert_function, tries=5)
