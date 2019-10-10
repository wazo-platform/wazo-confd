# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from ..helpers import scenarios as s
from . import confd


def test_put_errors():
    url = confd.asterisk.features.general.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'options', 123
    yield s.check_bogus_field_returns_error, url, 'options', None
    yield s.check_bogus_field_returns_error, url, 'options', 'string'
    yield s.check_bogus_field_returns_error, url, 'options', [['ordered', 'option']]
    yield s.check_bogus_field_returns_error, url, 'options', {'wrong_value': 23}
    yield s.check_bogus_field_returns_error, url, 'options', {'none_value': None}

    yield s.check_bogus_field_returns_error, url, 'options', {
        'comebacktoorigin': 'value'
    }
    yield s.check_bogus_field_returns_error, url, 'options', {'courtesytone': 'value'}
    yield s.check_bogus_field_returns_error, url, 'options', {'findslot': 'value'}
    yield s.check_bogus_field_returns_error, url, 'options', {
        'parkedcallhangup': 'value'
    }
    yield s.check_bogus_field_returns_error, url, 'options', {
        'parkedcallrecording': 'value'
    }
    yield s.check_bogus_field_returns_error, url, 'options', {
        'parkedcallreparking': 'value'
    }
    yield s.check_bogus_field_returns_error, url, 'options', {
        'parkedcalltransfers': 'value'
    }
    yield s.check_bogus_field_returns_error, url, 'options', {'parkeddynamic': 'value'}
    yield s.check_bogus_field_returns_error, url, 'options', {
        'parkedmusicclass': 'value'
    }
    yield s.check_bogus_field_returns_error, url, 'options', {'parkedplay': 'value'}
    yield s.check_bogus_field_returns_error, url, 'options', {'parkinghints': 'value'}
    yield s.check_bogus_field_returns_error, url, 'options', {'parkingtime': 'value'}
    yield s.check_bogus_field_returns_error, url, 'options', {'parkpos': 'value'}


def test_get():
    response = confd.asterisk.features.general.get()
    response.assert_ok()


def test_edit_features_general():
    parameters = {'options': {'nat': 'toto', 'username': 'Bob'}}

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
    yield s.check_bus_event, 'config.features_general.edited', url.put, {'options': {}}
