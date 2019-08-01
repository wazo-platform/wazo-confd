# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from . import confd
from ..helpers import scenarios as s


def test_put_errors():
    url = confd.asterisk.queues.general.put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'options', 123)
    s.check_bogus_field_returns_error(url, 'options', None)
    s.check_bogus_field_returns_error(url, 'options', 'string')
    s.check_bogus_field_returns_error(url, 'options', [['ordered', 'option']])
    s.check_bogus_field_returns_error(url, 'options', {'wrong_value': 23})
    s.check_bogus_field_returns_error(url, 'options', {'none_value': None})


def test_get():
    response = confd.asterisk.queues.general.get()
    response.assert_ok()


def test_edit_queue_general():
    parameters = {'options': {'nat': 'toto',
                              'username': 'Bob'}}

    response = confd.asterisk.queues.general.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.queues.general.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_queue_general_with_no_option():
    parameters = {'options': {}}
    response = confd.asterisk.queues.general.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.queues.general.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_queue_general_with_none_value():
    parameters = {'options': {'nat': 'value'}}

    response = confd.asterisk.queues.general.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.queues.general.get()
    assert_that(response.item, has_entries(parameters))


def test_bus_event_when_edited():
    url = confd.asterisk.queues.general
    s.check_bus_event('config.queue_general.edited', url.put, {'options': {}})
