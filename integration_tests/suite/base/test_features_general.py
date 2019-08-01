# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from ..helpers import scenarios as s
from . import confd


def test_put_errors():
    url = confd.asterisk.features.general.put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'options', 123)
    s.check_bogus_field_returns_error(url, 'options', None)
    s.check_bogus_field_returns_error(url, 'options', 'string')
    s.check_bogus_field_returns_error(url, 'options', [['ordered', 'option']])
    s.check_bogus_field_returns_error(url, 'options', {'wrong_value': 23})
    s.check_bogus_field_returns_error(url, 'options', {'none_value': None})

    s.check_bogus_field_returns_error(url, 'options', {'comebacktoorigin': 'value'})
    s.check_bogus_field_returns_error(url, 'options', {'courtesytone': 'value'})
    s.check_bogus_field_returns_error(url, 'options', {'findslot': 'value'})
    s.check_bogus_field_returns_error(url, 'options', {'parkedcallhangup': 'value'})
    s.check_bogus_field_returns_error(url, 'options', {'parkedcallrecording': 'value'})
    s.check_bogus_field_returns_error(url, 'options', {'parkedcallreparking': 'value'})
    s.check_bogus_field_returns_error(url, 'options', {'parkedcalltransfers': 'value'})
    s.check_bogus_field_returns_error(url, 'options', {'parkeddynamic': 'value'})
    s.check_bogus_field_returns_error(url, 'options', {'parkedmusicclass': 'value'})
    s.check_bogus_field_returns_error(url, 'options', {'parkedplay': 'value'})
    s.check_bogus_field_returns_error(url, 'options', {'parkinghints': 'value'})
    s.check_bogus_field_returns_error(url, 'options', {'parkingtime': 'value'})
    s.check_bogus_field_returns_error(url, 'options', {'parkpos': 'value'})


def test_get():
    response = confd.asterisk.features.general.get()
    response.assert_ok()


def test_edit_features_general():
    parameters = {'options': {'nat': 'toto',
                              'username': 'Bob'}}

    response = confd.asterisk.features.general.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.features.general.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_features_general_with_no_option():
    parameters = {'options': {}}
    response = confd.asterisk.features.general.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.features.general.get()
    assert_that(response.item, has_entries(parameters))


def test_bus_event_when_edited():
    url = confd.asterisk.features.general
    s.check_bus_event('config.features_general.edited', url.put, {'options': {}})
