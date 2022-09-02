# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from ..helpers import scenarios as s
from . import confd
from ..helpers.config import TOKEN_SUB_TENANT


REQUIRED_OPTIONS = {'atxfer': '*0', 'blindxfer': '9'}


def test_put_errors():
    url = confd.asterisk.features.featuremap.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'options', 123
    yield s.check_bogus_field_returns_error, url, 'options', None
    yield s.check_bogus_field_returns_error, url, 'options', 'string'
    yield s.check_bogus_field_returns_error, url, 'options', [['ordered', 'option']]
    yield s.check_bogus_field_returns_error, url, 'options', dict(
        wrong_value=23, **REQUIRED_OPTIONS
    )
    yield s.check_bogus_field_returns_error, url, 'options', dict(
        none_value=None, **REQUIRED_OPTIONS
    )

    regex = r'atxfer'
    yield s.check_bogus_field_returns_error_matching_regex, url, 'options', {
        'blindxfer': '1',
        'automixmon': '1',
    }, regex
    regex = r'blindxfer'
    yield s.check_bogus_field_returns_error_matching_regex, url, 'options', {
        'atxfer': '1',
        'automixmon': '1',
    }, regex


def test_get():
    response = confd.asterisk.features.featuremap.get()
    response.assert_ok()


def test_edit_features_featuremap():
    options = dict(toto='titi', **REQUIRED_OPTIONS)
    parameters = {'options': options}

    response = confd.asterisk.features.featuremap.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.features.featuremap.get()
    assert_that(response.item, has_entries(parameters))


def test_restrict_only_master_tenant():
    response = confd.asterisk.features.featuremap.get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.asterisk.features.featuremap.put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)


def test_bus_event_when_edited():
    url = confd.asterisk.features.featuremap
    headers = {}

    yield s.check_event, 'features_featuremap_edited', headers, url.put, {
        'options': REQUIRED_OPTIONS
    }
