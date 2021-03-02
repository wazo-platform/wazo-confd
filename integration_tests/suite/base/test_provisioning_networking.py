# Copyright 2019-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from . import confd
from ..helpers.config import TOKEN_SUB_TENANT


def test_get():
    response = confd.provisioning.networking.get()
    assert_that(
        response.item,
        has_entries({'provision_host': '', 'provision_http_port': 8667}),
    )


def test_put_minimal_parameters():
    body = {}
    result = confd.provisioning.networking.put(body)
    result.assert_status(204)
    response = confd.provisioning.networking.get()
    assert_that(
        response.item,
        has_entries({'provision_host': '', 'provision_http_port': 8667}),
    )

    body = {'provision_host': '127.0.0.1'}
    result = confd.provisioning.networking.put(body)
    result.assert_status(204)
    response = confd.provisioning.networking.get()
    assert_that(
        response.item,
        has_entries({'provision_host': '127.0.0.1', 'provision_http_port': 8667}),
    )

    body = {'provision_host': None}
    result = confd.provisioning.networking.put(body)
    result.assert_status(204)
    response = confd.provisioning.networking.get()
    assert_that(
        response.item,
        has_entries({'provision_host': None, 'provision_http_port': 8667}),
    )


def test_put_all_parameters():
    body = {
        'provision_host': '127.0.0.1',
        'provision_http_port': 8665,
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
