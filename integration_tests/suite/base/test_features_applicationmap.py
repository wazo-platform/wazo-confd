# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from ..helpers import scenarios as s
from ..helpers.config import TOKEN_SUB_TENANT
from . import confd

REQUIRED_OPTIONS = {'togglerecord': '*3,self,AGI(localhost,...)'}


def test_put_errors():
    url = confd.asterisk.features.applicationmap.put
    yield from error_checks(url)


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'options', 123
    yield s.check_bogus_field_returns_error, url, 'options', None
    yield s.check_bogus_field_returns_error, url, 'options', 'string'
    yield s.check_bogus_field_returns_error, url, 'options', [['ordered', 'option']]
    yield s.check_bogus_field_returns_error, url, 'options', {
        'wrong_value': 23,
        **REQUIRED_OPTIONS,
    }
    yield s.check_bogus_field_returns_error, url, 'options', {
        'none_value': None,
        **REQUIRED_OPTIONS,
    }


def test_get():
    response = confd.asterisk.features.applicationmap.get()
    response.assert_ok()


def test_edit_features_applicationmap():
    parameters = {'options': {'nat': 'toto', 'username': 'Bob', **REQUIRED_OPTIONS}}

    response = confd.asterisk.features.applicationmap.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.features.applicationmap.get()
    assert_that(response.item, has_entries(parameters))


def test_restrict_only_master_tenant():
    response = confd.asterisk.features.applicationmap.get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.asterisk.features.applicationmap.put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)


def test_bus_event_when_edited():
    url = confd.asterisk.features.applicationmap
    headers = {}

    yield s.check_event, 'features_applicationmap_edited', headers, url.put, {
        'options': REQUIRED_OPTIONS
    }
