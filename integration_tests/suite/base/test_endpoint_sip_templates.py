# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    has_entries,
    has_entry,
    has_items,
    has_length,
    instance_of,
    none,
    not_,
    not_none,
)

from . import confd
from ..helpers import errors as e, fixtures
from ..helpers.config import MAIN_TENANT


@fixtures.sip_template()
@fixtures.sip_template()
def test_list_templates(template1, template2):
    response = confd.endpoints.sip.templates.get()
    assert_that(
        response.items,
        has_items(
            has_entry('uuid', template1['uuid']), has_entry('uuid', template2['uuid'])
        ),
    )

    response = confd.endpoints.sip.templates.get(search=template1['name'])
    assert_that(response.items, contains(has_entry('uuid', template1['uuid'])))

    response = confd.endpoints.sip.get()
    assert_that(
        response.items,
        not_(
            contains_inanyorder(
                has_entry('uuid', template1['uuid']),
                has_entry('uuid', template2['uuid']),
            )
        ),
    )


@fixtures.sip_template()
@fixtures.sip()
def test_get_templates(template, sip):
    response = confd.endpoints.sip.templates(template['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            uuid=not_none(),
            name=has_length(8),
            label=None,
            aor_section_options=instance_of(list),
            auth_section_options=instance_of(list),
            endpoint_section_options=instance_of(list),
            identify_section_options=instance_of(list),
            registration_section_options=instance_of(list),
            registration_outbound_auth_section_options=instance_of(list),
            outbound_auth_section_options=instance_of(list),
            templates=instance_of(list),
            trunk=None,
            line=None,
            transport=None,
            context=None,
            asterisk_id=None,
        ),
    )

    response = confd.endpoints.sip.templates(sip['uuid']).get()
    response.assert_match(404, e.not_found())


def test_create_template_minimal_parameters():
    response = confd.endpoints.sip.templates.post()

    response.assert_created()
    assert_that(
        response.item,
        has_entries(
            uuid=not_none(),
            tenant_uuid=MAIN_TENANT,
            name=not_none(),
            label=none(),
            aor_section_options=empty(),
            auth_section_options=empty(),
            endpoint_section_options=empty(),
            identify_section_options=empty(),
            registration_section_options=empty(),
            registration_outbound_auth_section_options=empty(),
            outbound_auth_section_options=empty(),
            templates=empty(),
            asterisk_id=none(),
        ),
    )


@fixtures.context()
@fixtures.transport()
@fixtures.sip_template()
@fixtures.sip_template()
def test_create_template_all_parameters(context, transport, endpoint_1, endpoint_2):
    response = confd.endpoints.sip.templates.post(
        name="template_name",
        label="label",
        aor_section_options=[
            ['qualify_frequency', '60'],
            ['maximum_expiration', '3600'],
            ['remove_existing', 'yes'],
            ['max_contacts', '1'],
        ],
        auth_section_options=[['username', 'yiq8yej0'], ['password', 'yagq7x0w']],
        endpoint_section_options=[
            ['force_rport', 'yes'],
            ['rewrite_contact', 'yes'],
            ['callerid', '"Firstname Lastname" <100>'],
        ],
        identify_section_options=[
            ['match', '54.172.60.0'],
            ['match', '54.172.60.1'],
            ['match', '54.172.60.2'],
        ],
        registration_section_options=[
            ['client_uri', 'sip:peer@proxy.example.com'],
            ['server_uri', 'sip:proxy.example.com'],
            ['expiration', '120'],
        ],
        registration_outbound_auth_section_options=[
            ['username', 'outbound-registration-username'],
            ['password', 'outbound-registration-password'],
        ],
        outbound_auth_section_options=[
            ['username', 'outbound-auth'],
            ['password', 'outbound-password'],
        ],
        context=context,
        transport=transport,
        templates=[endpoint_1, endpoint_2],
        asterisk_id='asterisk_id',
    )

    assert_that(
        response.item,
        has_entries(
            tenant_uuid=MAIN_TENANT,
            name='template_name',
            label='label',
            aor_section_options=[
                ['qualify_frequency', '60'],
                ['maximum_expiration', '3600'],
                ['remove_existing', 'yes'],
                ['max_contacts', '1'],
            ],
            auth_section_options=[['username', 'yiq8yej0'], ['password', 'yagq7x0w']],
            endpoint_section_options=[
                ['force_rport', 'yes'],
                ['rewrite_contact', 'yes'],
                ['callerid', '"Firstname Lastname" <100>'],
            ],
            identify_section_options=[
                ['match', '54.172.60.0'],
                ['match', '54.172.60.1'],
                ['match', '54.172.60.2'],
            ],
            registration_section_options=[
                ['client_uri', 'sip:peer@proxy.example.com'],
                ['server_uri', 'sip:proxy.example.com'],
                ['expiration', '120'],
            ],
            registration_outbound_auth_section_options=[
                ['username', 'outbound-registration-username'],
                ['password', 'outbound-registration-password'],
            ],
            outbound_auth_section_options=[
                ['username', 'outbound-auth'],
                ['password', 'outbound-password'],
            ],
            context=has_entries(id=context['id']),
            transport=has_entries(uuid=transport['uuid']),
            templates=contains(
                has_entries(uuid=endpoint_1['uuid']),
                has_entries(uuid=endpoint_2['uuid']),
            ),
            asterisk_id='asterisk_id',
        ),
    )


@fixtures.sip_template()
@fixtures.sip()
def test_edit_template(template, sip):
    response = confd.endpoints.sip.templates(template['uuid']).put()
    response.assert_updated()

    response = confd.endpoints.sip.templates(sip['uuid']).put()
    response.assert_match(404, e.not_found())


@fixtures.sip_template()
@fixtures.sip()
def test_delete_template(template, sip):
    response = confd.endpoints.sip.templates(template['uuid']).delete()
    response.assert_deleted()

    response = confd.endpoints.sip.templates(sip['uuid']).delete()
    response.assert_match(404, e.not_found())
