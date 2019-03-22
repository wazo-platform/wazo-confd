# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import (
    assert_that,
    has_entries,
)

from . import confd


def test_get():
    response = confd.provisioning.networking.get()
    assert_that(response.item, has_entries({
        'provision_ip': '',
        'provision_http_port': 8667,
        'rest_ip': 'provd',
        'rest_https_port': 8666,
    }))


def test_put_minimal_parameters():
    body = {}
    result = confd.provisioning.networking.put(body)
    result.assert_status(204)
    response = confd.provisioning.networking.get()
    assert_that(response.item, has_entries({
        'provision_ip': '',
        'provision_http_port': 8667,
        'rest_ip': 'provd',
        'rest_https_port': 8666,
    }))

    body = {
        'provision_ip': '127.0.0.1',
    }
    result = confd.provisioning.networking.put(body)
    result.assert_status(204)
    response = confd.provisioning.networking.get()
    assert_that(response.item, has_entries({
        'provision_ip': '127.0.0.1',
        'provision_http_port': 8667,
        'rest_ip': 'provd',
        'rest_https_port': 8666,
    }))


def test_put_all_parameters():
    body = {
        'provision_ip': '127.0.0.1',
        'provision_http_port': 8665,
        'rest_ip': '127.0.0.1',
        'rest_https_port': 8664,
    }
    result = confd.provisioning.networking.put(body)
    result.assert_status(204)
    response = confd.provisioning.networking.get()
    assert_that(response.item, has_entries(body))


def test_put_errors():
    # wrong ip address
    body = {
        'provision_ip': 'abcd',
        'rest_ip': '10.0.0.254',
    }
    result = confd.provisioning.networking.put(body)
    result.assert_match(400, re.compile(re.escape('provision_ip')))

    # wrong ip address
    body = {
        'provision_ip': '10.0.0.254',
        'rest_ip': 'abcd',
    }
    result = confd.provisioning.networking.put(body)
    result.assert_match(400, re.compile(re.escape('rest_ip')))
