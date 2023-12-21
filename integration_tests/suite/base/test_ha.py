# Copyright 2019-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import assert_that, has_entries, has_entry, only_contains

from ..helpers.config import TOKEN_SUB_TENANT
from . import confd, sysconfd


def test_get():
    sysconfd.set_response(
        'get_ha_config', {'node_type': 'disabled', 'remote_address': None}
    )
    response = confd.ha.get()
    assert_that(
        response.item, has_entries({'node_type': 'disabled', 'remote_address': None})
    )


def test_put():
    # Disabling HA already disabled does not fail
    body = {'node_type': 'disabled'}
    result = confd.ha.put(body)

    result.assert_status(204)

    # Enable HA
    body = {'node_type': 'master', 'remote_address': '10.10.10.10'}
    result = confd.ha.put(body)

    result.assert_status(204)
    sysconfd.assert_request(
        '/update_ha_config',
        method='POST',
        json={'node_type': 'master', 'remote_address': '10.10.10.10'},
    )
    assert_that(
        confd.registrars.get().json,
        has_entry(
            'items',
            only_contains(
                has_entries(
                    {'backup_host': '10.10.10.10', 'proxy_backup_host': '10.10.10.10'}
                )
            ),
        ),
    )

    # Disable HA = reset sip/provd options to default
    body = {'node_type': 'disabled'}
    result = confd.ha.put(body)

    result.assert_status(204)
    sysconfd.assert_request(
        '/update_ha_config',
        method='POST',
        json={'node_type': 'disabled', 'remote_address': ''},
    )
    assert_that(
        confd.registrars.get().json,
        has_entry(
            'items',
            only_contains(
                has_entries({'backup_host': None, 'proxy_backup_host': None})
            ),
        ),
    )


def test_put_errors():
    # missing keys
    body = {}
    result = confd.ha.put(body)
    result.assert_match(400, re.compile(re.escape('node_type')))

    # missing keys
    body = {'node_type': 'master'}
    result = confd.ha.put(body)
    result.assert_match(400, re.compile(re.escape('remote_address')))

    # null keys
    body = {'node_type': 'master', 'remote_address': None}
    result = confd.ha.put(body)
    result.assert_match(400, re.compile(re.escape('remote_address')))

    # invalid keys
    body = {'node_type': 'master', 'remote_address': 'not-an-ip-address'}
    result = confd.ha.put(body)
    result.assert_match(400, re.compile(re.escape('remote_address')))


def test_restrict_only_master_tenant():
    response = confd.ha.get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.ha.put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)
