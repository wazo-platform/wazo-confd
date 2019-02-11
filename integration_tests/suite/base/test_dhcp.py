# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import (
    all_of,
    assert_that,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    not_,
)

from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s,
)
from . import confd


def test_get():
    response = confd.dhcp.get()
    assert_that(response.item, has_entries({
        'active': False,
        'pool_start': '',
        'pool_end': '',
        'extra_network_interfaces': [],
    }))


def test_put_minimal_parameters():
    body = {
        'active': False
    }
    result = confd.dhcp.put(body)
    result.assert_status(204)
    response = confd.dhcp.get()
    assert_that(response.item, has_entries(body))

    body = {
        'active': True,
        'pool_start': '10.0.0.1',
        'pool_end': '10.0.0.254',
    }
    result = confd.dhcp.put(body)
    result.assert_status(204)
    response = confd.dhcp.get()
    assert_that(response.item, has_entries(body))


def test_put_all_parameters():
    body = {
        'active': True,
        'pool_start': '10.0.0.1',
        'pool_end': '10.0.0.254',
        'extra_network_interfaces': ['ens0p2', 'ens0p3'],
    }
    result = confd.dhcp.put(body)
    result.assert_status(204)
    response = confd.dhcp.get()
    assert_that(response.item, has_entries(body))


def test_put_errors():
    # missing keys
    body = {
        'active': True,
    }
    result = confd.dhcp.put(body)
    result.assert_match(400, re.compile(re.escape('pool_start')))

    # wrong ip address
    body = {
        'active': True,
        'pool_start': 'abcd',
        'pool_end': '10.0.0.254',
    }
    result = confd.dhcp.put(body)
    result.assert_match(400, re.compile(re.escape('pool_start')))

    # wrong ip address
    body = {
        'active': True,
        'pool_start': '10.0.0.1',
        'pool_end': 'abcd',
    }
    result = confd.dhcp.put(body)
    result.assert_match(400, re.compile(re.escape('pool_end')))

    # pool_start > pool_end
    body = {
        'active': True,
        'pool_start': '10.0.0.2',
        'pool_end': '10.0.0.1',
    }
    result = confd.dhcp.put(body)
    result.assert_match(400, re.compile(re.escape('pool_end')))
