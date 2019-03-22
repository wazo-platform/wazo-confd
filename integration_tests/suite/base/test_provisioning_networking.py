# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_entries,
)

from . import confd


def test_get():
    response = confd.provisioning.networking.get()
    assert_that(response.item, has_entries({
        'provision_host': '',
        'provision_http_port': 8667,
        'rest_host': 'provd',
        'rest_https_port': 8666,
    }))


def test_put_minimal_parameters():
    body = {}
    result = confd.provisioning.networking.put(body)
    result.assert_status(204)
    response = confd.provisioning.networking.get()
    assert_that(response.item, has_entries({
        'provision_host': '',
        'provision_http_port': 8667,
        'rest_host': 'provd',
        'rest_https_port': 8666,
    }))

    body = {
        'provision_host': '127.0.0.1',
    }
    result = confd.provisioning.networking.put(body)
    result.assert_status(204)
    response = confd.provisioning.networking.get()
    assert_that(response.item, has_entries({
        'provision_host': '127.0.0.1',
        'provision_http_port': 8667,
        'rest_host': 'provd',
        'rest_https_port': 8666,
    }))


def test_put_all_parameters():
    body = {
        'provision_host': '127.0.0.1',
        'provision_http_port': 8665,
        'rest_host': '127.0.0.1',
        'rest_https_port': 8664,
    }
    result = confd.provisioning.networking.put(body)
    result.assert_status(204)
    response = confd.provisioning.networking.get()
    assert_that(response.item, has_entries(body))
