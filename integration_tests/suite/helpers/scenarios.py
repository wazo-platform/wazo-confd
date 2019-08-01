# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re
import random
import string

from hamcrest import assert_that, contains, has_length, has_entries
from xivo_test_helpers import until

from .bus import BusClient

from . import errors as e


def check_resource_not_found(request, resource):
    response = request()
    response.assert_match(404, e.not_found(resource=resource))


def check_missing_required_field_returns_error(request, field):
    response = request({field: None})
    response.assert_match(400, re.compile(re.escape(field)))


def check_bogus_field_returns_error(request, field, bogus, required_field=None, message=None):
    message = message or field
    body = required_field if required_field else {}
    body[field] = bogus
    response = request(body)
    response.assert_match(400, re.compile(re.escape(message)))


def check_bogus_field_returns_error_matching_regex(request, field, bogus, regex):
    response = request({field: bogus})
    response.assert_match(400, re.compile(regex))


def random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def random_digits(length):
    return ''.join(random.choice(string.digits) for _ in range(length))


def check_bus_event(routing_key, url, body=None):
    bus_events = BusClient.accumulator(routing_key)
    url(body) if body else url()

    def assert_function():
        assert_that(bus_events.accumulate(), has_length(1))

    until.assert_(assert_function, tries=5)


def search_error_checks(url):
    check_bogus_query_string_returns_error(url, 'order', 'invalid_column')
    check_bogus_query_string_returns_error(url, 'direction', 'invalid')
    check_bogus_query_string_returns_error(url, 'limit', -42)
    check_bogus_query_string_returns_error(url, 'limit', 'invalid')
    check_bogus_query_string_returns_error(url, 'skip', -42)
    check_bogus_query_string_returns_error(url, 'skip', 'invalid')
    check_bogus_query_string_returns_error(url, 'offset', -42)
    check_bogus_query_string_returns_error(url, 'offset', 'invalid')


def check_bogus_query_string_returns_error(request, query_string, bogus):
    response = request(**{query_string: bogus})
    response.assert_match(400, re.compile(re.escape(query_string)))


def check_sorting(url, resource1, resource2, field, search, id_field='id'):
    response = url(search=search, order=field, direction='asc')
    assert_that(response.items, contains(has_entries(**{id_field: resource1[id_field]}),
                                         has_entries(**{id_field: resource2[id_field]})))

    response = url(search=search, order=field, direction='desc')
    assert_that(response.items, contains(has_entries(**{id_field: resource2[id_field]}),
                                         has_entries(**{id_field: resource1[id_field]})))


def check_offset(url, resource1, resource2, field, search, id_field='id'):
    response = url(search=search, order=field, offset=1)
    assert_that(response.items, contains(has_entries(**{id_field: resource2[id_field]})))


def check_offset_legacy(url, resource1, resource2, field, search, id_field='id'):
    response = url(search=search, order=field, skip=1)
    assert_that(response.items, contains(has_entries(**{id_field: resource2[id_field]})))


def check_limit(url, resource1, resource2, field, search, id_field='id'):
    response = url(search=search, order=field, limit=1)
    assert_that(response.items, contains(has_entries(**{id_field: resource1[id_field]})))
