# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import assert_that, has_entries

from . import confd
from ..helpers.config import TOKEN_SUB_TENANT


def test_get():
    response = confd.emails.get()
    assert_that(
        response.item,
        has_entries(
            {
                'domain_name': '',
                'from': 'example.wazo.community',
                'address_rewriting_rules': [],
                'smtp_host': '',
                'fallback_smtp_host': '',
            }
        ),
    )


def test_put_minimal_parameters():
    body = {}
    result = confd.emails.put(body)
    result.assert_status(204)
    response = confd.emails.get()
    assert_that(response.item, has_entries(body))


def test_put_all_parameters():
    body = {
        'domain_name': 'test.com',
        'from': 'a.test.com',
        'address_rewriting_rules': [
            {'match': 'test1', 'replacement': 'test1@test.com'},
            {'match': 'test2', 'replacement': 'test2@test.com'},
        ],
        'smtp_host': 'smtp.test.com',
        'fallback_smtp_host': 'smtp2.test.com',
    }
    result = confd.emails.put(body)
    result.assert_status(204)
    response = confd.emails.get()
    assert_that(response.item, has_entries(body))


def test_put_errors():
    fields_too_long = ['domain_name', 'from', 'smtp_host', 'fallback_smtp_host']
    for field in fields_too_long:
        body = {field: 'a' * 256}
        result = confd.emails.put(body)
        result.assert_match(400, re.compile(re.escape(field)))


def test_restrict_only_master_tenant():
    response = confd.emails.get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.emails.put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)
