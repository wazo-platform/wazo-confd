# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import (
    assert_that,
    has_entries,
)

from . import confd
from . import sysconfd


def test_get():
    sysconfd.set_response('get_ha_config', {
        'node_type': 'disabled',
        'remote_address': None,
    })
    response = confd.ha.get()
    assert_that(response.item, has_entries({
        'node_type': 'disabled',
        'remote_address': None,
    }))


def test_put():
    body = {
        'node_type': 'disabled',
    }
    result = confd.ha.put(body)
    result.assert_status(204)
    sysconfd.assert_request('/update_ha_config', method='POST', json={'node_type': 'disabled', 'remote_address': ''})

    body = {
        'node_type': 'master',
        'remote_address': '10.10.10.10',
    }
    result = confd.ha.put(body)
    result.assert_status(204)
    sysconfd.assert_request('/update_ha_config', method='POST', json={'node_type': 'master', 'remote_address': '10.10.10.10'})


def test_put_errors():
    # missing keys
    body = {}
    result = confd.ha.put(body)
    result.assert_match(400, re.compile(re.escape('node_type')))

    # missing keys
    body = {
        'node_type': 'master',
    }
    result = confd.ha.put(body)
    result.assert_match(400, re.compile(re.escape('remote_address')))

    # null keys
    body = {
        'node_type': 'master',
        'remote_address': None,
    }
    result = confd.ha.put(body)
    result.assert_match(400, re.compile(re.escape('remote_address')))

    # invalid keys
    body = {
        'node_type': 'master',
        'remote_address': 'not-an-ip-address',
    }
    result = confd.ha.put(body)
    result.assert_match(400, re.compile(re.escape('remote_address')))
