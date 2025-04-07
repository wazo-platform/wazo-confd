# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import re
import string
from datetime import datetime

from hamcrest import all_of, assert_that, contains, has_entries, has_items
from wazo_test_helpers import until

from . import errors as e
from .bus import BusClient

OVERHEAD_DB_REQUESTS = 3  # BEGIN, SELECT 1, COMMIT


def check_resource_not_found(request, resource):
    response = request()
    response.assert_match(404, e.not_found(resource=resource))


def check_missing_required_field_returns_error(request, field):
    response = request({field: None})
    response.assert_match(400, re.compile(re.escape(field)))


def check_bogus_field_returns_error(
    request, field, bogus, required_field=None, message=None
):
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


def check_event(event_name, expected_headers, url, body=None):
    expected_headers = {
        'name': event_name,
        'required_access': f'event.{event_name}',
        **expected_headers,
    }

    accumulator = BusClient.accumulator(
        headers={'name': event_name},
    )
    result = url(body) if body else url()

    assertions = all_of(
        has_items(
            has_entries(
                headers=has_entries(
                    expected_headers,
                )
            )
        )
    )

    def check_bus():
        assert_that(accumulator.accumulate(with_headers=True), assertions)

    until.assert_(check_bus, tries=5)

    return result


def search_error_checks(url):
    check_bogus_query_string_returns_error(url, 'order', 'invalid_column')
    check_bogus_query_string_returns_error(url, 'direction', 'invalid')
    check_bogus_query_string_returns_error(url, 'limit', -42)
    check_bogus_query_string_returns_error(url, 'limit', 'invalid')
    check_bogus_query_string_returns_error(url, 'offset', -42)
    check_bogus_query_string_returns_error(url, 'offset', 'invalid')


def check_bogus_query_string_returns_error(request, query_string, bogus):
    response = request(**{query_string: bogus})
    response.assert_match(400, re.compile(re.escape(query_string)))


def check_sorting(url, resource1, resource2, field, search, id_field='id'):
    response = url(search=search, order=field, direction='asc')
    assert_that(
        response.items,
        contains(
            has_entries(**{id_field: resource1[id_field]}),
            has_entries(**{id_field: resource2[id_field]}),
        ),
    )

    response = url(search=search, order=field, direction='desc')
    assert_that(
        response.items,
        contains(
            has_entries(**{id_field: resource2[id_field]}),
            has_entries(**{id_field: resource1[id_field]}),
        ),
    )


def check_offset(url, resource1, resource2, field, search, id_field='id'):
    response = url(search=search, order=field, offset=1)
    assert_that(
        response.items, contains(has_entries(**{id_field: resource2[id_field]}))
    )


def check_limit(url, resource1, resource2, field, search, id_field='id'):
    response = url(search=search, order=field, limit=1)
    assert_that(
        response.items, contains(has_entries(**{id_field: resource1[id_field]}))
    )


def check_db_requests(cls, url, nb_requests, **kwargs):
    time_start = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    # "REFRESH MATERIALIZED VIEW" happens at unpredictable times
    nb_logs_start = cls.count_database_logs(
        since=time_start, exclude='REFRESH MATERIALIZED VIEW'
    )
    url(**kwargs)
    nb_logs_end = cls.count_database_logs(
        since=time_start, exclude='REFRESH MATERIALIZED VIEW'
    )
    actual_count = nb_logs_end - nb_logs_start
    expected_count = OVERHEAD_DB_REQUESTS + nb_requests
    assert (
        expected_count == actual_count
    ), f'Expected: {expected_count} Count: {actual_count}\n{cls.database_logs(service_name="postgres", since=time_start)}'
