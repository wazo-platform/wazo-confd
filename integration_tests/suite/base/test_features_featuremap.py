# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from ..helpers import scenarios as s
from . import confd


REQUIRED_OPTIONS = {'atxfer': '*0',
                    'blindxfer': '9',
                    'automixmon': '#7'}


def test_put_errors():
    url = confd.asterisk.features.featuremap.put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'options', 123)
    s.check_bogus_field_returns_error(url, 'options', None)
    s.check_bogus_field_returns_error(url, 'options', 'string')
    s.check_bogus_field_returns_error(url, 'options', [['ordered', 'option']])
    s.check_bogus_field_returns_error(url, 'options', dict(wrong_value=23, **REQUIRED_OPTIONS))
    s.check_bogus_field_returns_error(url, 'options', dict(none_value=None, **REQUIRED_OPTIONS))

    regex = r'atxfer'
    s.check_bogus_field_returns_error_matching_regex(
        url, 'options', {'blindxfer': '1', 'automixmon': '1'}, regex
    )
    regex = r'blindxfer'
    s.check_bogus_field_returns_error_matching_regex(
        url, 'options', {'atxfer': '1', 'automixmon': '1'}, regex
    )
    regex = r'automixmon'
    s.check_bogus_field_returns_error_matching_regex(
        url, 'options', {'blindxfer': '1', 'atxfer': '1'}, regex
    )


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


def test_bus_event_when_edited():
    url = confd.asterisk.features.featuremap
    s.check_bus_event('config.features_featuremap.edited', url.put, {'options': REQUIRED_OPTIONS})
