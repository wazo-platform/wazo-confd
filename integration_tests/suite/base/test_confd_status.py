# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from . import confd

from hamcrest import (
    assert_that,
    has_entries,
)

def test_confd_status_is_ok():
    expected_entries = {
        'bus_consumer': {
            'status': 'ok',
        },
        'master_tenant': {
            'status': 'ok',
        },
        'rest_api': {
            'status': 'ok',
        },
        'service_token': {
            'status': 'ok',
        },
    }
    response = confd.status.get()
    assert_that(response.item, has_entries(**expected_entries))


