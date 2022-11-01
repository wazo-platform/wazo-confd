# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import (
    assert_that,
    contains_inanyorder,
    has_entries,
)

from . import confd
from ..helpers.config import CONTEXT


def test_create_line_with_multiple_endpoints_error():
    endpoint_sip_body = {'name': "name"}
    endpoint_sccp_body = {'options': []}
    endpoint_custom_body = {'interface': 'custom/createall'}

    response = confd.lines.post(
        context=CONTEXT,
        endpoint_sip=endpoint_sip_body,
        endpoint_sccp=endpoint_sccp_body,
    )
    matcher = re.compile(re.escape('Only one endpoint should be configured on a line'))
    response.assert_match(400, matcher)

    response = confd.lines.post(
        context=CONTEXT,
        endpoint_sip=endpoint_sip_body,
        endpoint_custom=endpoint_custom_body,
    )
    response.assert_match(400, matcher)

    response = confd.lines.post(
        context=CONTEXT,
        endpoint_custom=endpoint_custom_body,
        endpoint_sccp=endpoint_sccp_body,
    )
    response.assert_match(400, matcher)


def test_create_line_endpoint_sccp_with_caller_id():
    endpoint_sccp_no_cid_body = {'options': []}

    response = confd.lines.post(
        context=CONTEXT,
        caller_id_name='Foobar',
        # caller_id_num='1004',  # SCCP is incompatible with a caller id num
        endpoint_sccp=endpoint_sccp_no_cid_body,
    )

    try:
        assert_that(
            response.item,
            has_entries(
                caller_id_name='Foobar',
                endpoint_sccp=has_entries(
                    options=contains_inanyorder(
                        ['cid_name', 'Foobar'],
                    ),
                ),
            ),
        )

        assert_that(
            confd.lines(response.item['id']).get().item,
            has_entries(
                caller_id_name='Foobar',
            ),
        )
        assert_that(
            confd.endpoints.sccp(response.item['endpoint_sccp']['id']).get().item,
            has_entries(
                options=contains_inanyorder(
                    ['cid_name', 'Foobar'],
                )
            ),
        )
    finally:
        confd.lines(response.item['id']).delete()

    endpoint_sccp_body = {
        'options': [
            ['cid_name', 'Lol'],
        ],
    }
    response = confd.lines.post(
        context=CONTEXT,
        caller_id_name='Foobar',
        # caller_id_num='1004',  # SCCP is incompatible with a caller id num
        endpoint_sccp=endpoint_sccp_body,
    )

    matcher = re.compile(re.escape('Ambiguous caller ID'))
    response.assert_match(400, matcher)


def test_create_line_endpoint_sip_with_caller_id():
    endpoint_sip_no_cid_body = {'name': 'no-cid'}

    response = confd.lines.post(
        context=CONTEXT,
        caller_id_name='Foobar',
        caller_id_num='1004',
        endpoint_sip=endpoint_sip_no_cid_body,
    )

    try:
        assert_that(
            response.item,
            has_entries(
                caller_id_name='Foobar',
                caller_id_num='1004',
                endpoint_sip=has_entries(
                    endpoint_section_options=contains_inanyorder(
                        ['callerid', '"Foobar" <1004>'],
                    ),
                ),
            ),
        )

        assert_that(
            confd.lines(response.item['id']).get().item,
            has_entries(
                caller_id_name='Foobar',
                caller_id_num='1004',
            ),
        )
        assert_that(
            confd.endpoints.sip(response.item['endpoint_sip']['uuid']).get().item,
            has_entries(
                endpoint_section_options=contains_inanyorder(
                    ['callerid', '"Foobar" <1004>'],
                ),
            ),
        )
    finally:
        confd.lines(response.item['id']).delete()

    endpoint_sip_body = {
        'endpoint_section_options': [
            ['callerid', '"what" <666>'],
        ],
    }
    response = confd.lines.post(
        context=CONTEXT,
        caller_id_name='Foobar',
        caller_id_num='1004',
        endpoint_sip=endpoint_sip_body,
    )

    matcher = re.compile(re.escape('Ambiguous caller ID'))
    response.assert_match(400, matcher)
