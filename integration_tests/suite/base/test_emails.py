# Copyright 2021-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import assert_that, has_entries

from ..helpers import scenarios as s
from ..helpers.config import TOKEN_SUB_TENANT
from . import confd


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
        'domain_name': 'example.org',
        'from': 'a.example.org',
        'address_rewriting_rules': [
            {'match': 'test1', 'replacement': 'test1@example.org'},
            {'match': 'test2', 'replacement': 'test2@example.org'},
        ],
        'smtp_host': 'smtp.example.org',
        'fallback_smtp_host': 'smtp2.example.org',
    }
    result = confd.emails.put(body)
    result.assert_status(204)
    response = confd.emails.get()
    assert_that(response.item, has_entries(body))


def test_put_errors():
    s.check_missing_body_returns_error(confd.emails, 'PUT')

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
