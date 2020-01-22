# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import (
    any_of,
    assert_that,
    only_contains,
    greater_than,
    has_entry,
    has_entries,
    has_key,
    has_length,
    not_,
)

from . import confd
from . import sysconfd


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
    sip_general_options = confd.asterisk.sip.general.get().json
    assert_that(sip_general_options, has_entry('options', has_length(greater_than(3))))  # other options are still present
    assert_that(sip_general_options, has_entry('options', has_entries({
        'minexpiry': '180',
        'maxexpiry': '300',
        'defaultexpiry': '240',
    })))
    assert_that(confd.registrars.get().json, has_entry('items', only_contains(has_entries({
        'backup_host': '10.10.10.10',
        'proxy_backup_host': '10.10.10.10',
    }))))

    # Disable HA = reset sip/provd options to default
    body = {'node_type': 'disabled'}
    result = confd.ha.put(body)

    result.assert_status(204)
    sysconfd.assert_request(
        '/update_ha_config',
        method='POST',
        json={'node_type': 'disabled', 'remote_address': ''},
    )
    sip_general_options = confd.asterisk.sip.general.get().json
    assert_that(sip_general_options, has_entry('options', has_length(greater_than(3))))  # other options are still present
    assert_that(sip_general_options, has_entry('options', has_entries({
        'minexpiry': '60',
        'maxexpiry': '3600',
        'defaultexpiry': '120',
    })))
    assert_that(confd.registrars.get().json, has_entry('items', only_contains(has_entries({
        'backup_host': None,
        'proxy_backup_host': None,
    }))))


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
