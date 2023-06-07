# Copyright 2019-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import assert_that, has_entries

from . import confd, sysconfd
from ..helpers.config import TOKEN_SUB_TENANT


def test_get():
    response = confd.dhcp.get()
    assert_that(
        response.item,
        has_entries(
            {
                'active': False,
                'pool_start': '',
                'pool_end': '',
                'network_interfaces': [],
            }
        ),
    )


def test_put_minimal_parameters():
    body = {'active': False}
    result = confd.dhcp.put(body)
    result.assert_status(204)
    response = confd.dhcp.get()
    assert_that(response.item, has_entries(body))

    body = {'active': True, 'pool_start': '10.0.0.1', 'pool_end': '10.0.0.254'}
    result = confd.dhcp.put(body)
    result.assert_status(204)
    response = confd.dhcp.get()
    assert_that(response.item, has_entries(body))


def test_put_all_parameters():
    sysconfd.set_response(
        'networking/interfaces',
        {
            'data': [
                {'name': 'ens0p2', 'address': '00:00:00:00:00:00'},
                {'name': 'ens0p3', 'address': '00:11:22:33:44:55'},
            ]
        },
    )
    body = {
        'active': True,
        'pool_start': '10.0.0.1',
        'pool_end': '10.0.0.254',
        'network_interfaces': ['ens0p2', 'ens0p3'],
    }
    result = confd.dhcp.put(body)
    result.assert_status(204)
    response = confd.dhcp.get()
    assert_that(response.item, has_entries(body))


def test_put_errors():
    # missing keys
    body = {'active': True}
    result = confd.dhcp.put(body)
    result.assert_match(400, re.compile(re.escape('pool_start')))

    # wrong ip address
    body = {'active': True, 'pool_start': 'abcd', 'pool_end': '10.0.0.254'}
    result = confd.dhcp.put(body)
    result.assert_match(400, re.compile(re.escape('pool_start')))

    # wrong ip address
    body = {'active': True, 'pool_start': '10.0.0.1', 'pool_end': 'abcd'}
    result = confd.dhcp.put(body)
    result.assert_match(400, re.compile(re.escape('pool_end')))

    # pool_start > pool_end
    body = {'active': True, 'pool_start': '10.0.0.2', 'pool_end': '10.0.0.1'}
    result = confd.dhcp.put(body)
    result.assert_match(400, re.compile(re.escape('pool_end')))

    # wrong network interface name
    sysconfd.set_response(
        'networking/interfaces',
        {
            'data': [
                {'name': 'lo', 'address': '00:00:00:00:00:00'},
                {'name': 'eth0', 'address': '00:11:22:33:44:55'},
            ]
        },
    )
    body = {
        'active': True,
        'network_interfaces': ['not-an-interface', 'lo'],
        'pool_start': '10.0.0.1',
        'pool_end': '10.0.0.254',
    }
    result = confd.dhcp.put(body)
    result.assert_match(400, re.compile(r'Invalid network interfaces'))


def test_restrict_only_master_tenant():
    response = confd.dhcp.get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.dhcp.put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)
