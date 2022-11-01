# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import (
    assert_that,
    contains_inanyorder,
    has_entries,
)

from . import confd
from ..helpers import fixtures
from ..helpers.config import CONTEXT


@fixtures.transport()
@fixtures.sip_template()
@fixtures.sip_template()
@fixtures.registrar()
def test_create_line_with_multiple_endpoints_error(
    transport, template_1, template_2, registrar
):
    aor_section_options = [
        ['@custom_variable', 'custom'],
        ['qualify_frequency', '60'],
        ['maximum_expiration', '3600'],
        ['remove_existing', 'yes'],
        ['max_contacts', '1'],
    ]
    auth_section_options = [['username', 'yiq8yej0'], ['password', 'yagq7x0w']]
    endpoint_section_options = [
        ['@custom_variable', 'custom'],
        ['force_rport', 'yes'],
        ['rewrite_contact', 'yes'],
        ['callerid', '"Firstname Lastname" <100>'],
    ]
    identify_section_options = [
        ['match', '54.172.60.0'],
        ['match', '54.172.60.1'],
        ['match', '54.172.60.2'],
    ]
    registration_section_options = [
        ['client_uri', 'sip:peer@proxy.example.com'],
        ['server_uri', 'sip:proxy.example.com'],
        ['expiration', '120'],
    ]
    registration_outbound_auth_section_options = [
        ['username', 'outbound-registration-username'],
        ['password', 'outbound-registration-password'],
    ]
    outbound_auth_section_options = [
        ['username', 'outbound-auth'],
        ['password', 'outbound-password'],
    ]

    endpoint_sip_body = {
        'name': "name",
        'label': "label",
        'aor_section_options': aor_section_options,
        'auth_section_options': auth_section_options,
        'endpoint_section_options': endpoint_section_options,
        'identify_section_options': identify_section_options,
        'registration_section_options': registration_section_options,
        'registration_outbound_auth_section_options': registration_outbound_auth_section_options,
        'outbound_auth_section_options': outbound_auth_section_options,
        'transport': transport,
        'templates': [template_1, template_2],
        'asterisk_id': 'asterisk_id',
    }
    endpoint_sccp_body = {
        'options': [
            ["cid_name", "cid_name"],
            ["cid_num", "cid_num"],
            ["allow", "allow"],
            ["disallow", "disallow"],
        ],
    }
    endpoint_custom_body = {
        'interface': 'custom/createall',
        'enabled': False,
    }

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
    endpoint_sccp_no_cid_body = {
        'options': [
            ["allow", "allow"],
            ["disallow", "disallow"],
        ],
    }

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
                        ["allow", "allow"],
                        ["disallow", "disallow"],
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
                    ["allow", "allow"],
                    ["disallow", "disallow"],
                )
            ),
        )
    finally:
        confd.lines(response.item['id']).delete()

    endpoint_sccp_body = {
        'options': [
            ["allow", "allow"],
            ["disallow", "disallow"],
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
    endpoint_sip_no_cid_body = {
        'name': 'no-cid',
        'label': 'Endpoint without Caller-ID',
    }

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
