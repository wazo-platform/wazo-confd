# Copyright 2019-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from ..helpers import scenarios as s
from ..helpers.config import TOKEN_SUB_TENANT
from . import confd


def test_get():
    response = confd.provisioning.networking.get()
    assert_that(
        response.item,
        has_entries(
            {
                'provision_host': '',
                'provision_http_port': 8667,
                'provision_http_base_url': '',
            }
        ),
    )


def test_put_errors():
    url = confd.provisioning.networking.put

    yield s.check_bogus_field_returns_error, url, 'provision_http_base_url', 123
    yield s.check_bogus_field_returns_error, url, 'provision_http_base_url', True
    yield s.check_bogus_field_returns_error, url, 'provision_http_base_url', {}
    yield s.check_bogus_field_returns_error, url, 'provision_http_base_url', []
    yield s.check_bogus_field_returns_error, url, 'provision_http_base_url', s.random_string(
        256
    )

    yield s.check_bogus_field_returns_error, url, 'provision_host', 123
    yield s.check_bogus_field_returns_error, url, 'provision_host', True
    yield s.check_bogus_field_returns_error, url, 'provision_host', {}
    yield s.check_bogus_field_returns_error, url, 'provision_host', []
    yield s.check_bogus_field_returns_error, url, 'provision_host', s.random_string(40)


def test_put_minimal_parameters():
    body = {}
    result = confd.provisioning.networking.put(body)
    result.assert_status(204)
    response = confd.provisioning.networking.get()
    assert_that(
        response.item,
        has_entries(
            {
                'provision_host': '',
                'provision_http_port': 8667,
                'provision_http_base_url': '',
            }
        ),
    )

    body = {
        'provision_host': '127.0.0.1',
        'provision_http_base_url': 'http://example.com',
    }
    result = confd.provisioning.networking.put(body)
    result.assert_status(204)
    response = confd.provisioning.networking.get()
    assert_that(
        response.item,
        has_entries(
            {
                'provision_host': '127.0.0.1',
                'provision_http_port': 8667,
                'provision_http_base_url': 'http://example.com',
            }
        ),
    )

    body = {'provision_host': None, 'provision_http_base_url': None}
    result = confd.provisioning.networking.put(body)
    result.assert_status(204)
    response = confd.provisioning.networking.get()
    assert_that(
        response.item,
        has_entries(
            {
                'provision_host': None,
                'provision_http_port': 8667,
                'provision_http_base_url': None,
            }
        ),
    )


def test_put_all_parameters():
    body = {
        'provision_host': '127.0.0.1',
        'provision_http_port': 8665,
        'provision_http_base_url': 'http://example.com',
    }
    result = confd.provisioning.networking.put(body)
    result.assert_status(204)
    response = confd.provisioning.networking.get()
    assert_that(response.item, has_entries(body))


def test_restrict_only_master_tenant():
    response = confd.provisioning.networking.get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.provisioning.networking.put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)
