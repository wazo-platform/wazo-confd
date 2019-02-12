# -*- coding: utf-8 -*-
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
        'remote_address': '',
    })
    response = confd.ha.get()
    assert_that(response.item, has_entries({
        'node_type': 'disabled',
        'remote_address': '',
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
        'remote_address': 'slave.example.com',
    }
    result = confd.ha.put(body)
    result.assert_status(204)
    sysconfd.assert_request('/update_ha_config', method='POST',  json={'node_type': 'master', 'remote_address': 'slave.example.com'})


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
