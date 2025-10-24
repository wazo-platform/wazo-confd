# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import (
    all_of,
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    has_length,
    instance_of,
    is_not,
    none,
    not_,
    not_none,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import BaseIntegrationTest, confd

FAKE_UUID = '99999999-9999-4999-9999-999999999999'


def test_get_errors():
    fake_sip_get = confd.endpoints.sip.templates(FAKE_UUID).get
    s.check_resource_not_found(fake_sip_get, 'SIPEndpointTemplate')


@fixtures.sip_template()
def test_delete_errors(sip):
    url = confd.endpoints.sip.templates(sip['uuid'])
    url.delete()
    s.check_resource_not_found(url.get, 'SIPEndpointTemplate')


def test_post_errors():
    url = confd.endpoints.sip.templates
    error_checks(url.post)
    s.check_missing_body_returns_error(url, 'POST')


@fixtures.sip_template()
def test_put_errors(sip):
    url = confd.endpoints.sip.templates(sip['uuid'])
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')

    s.check_bogus_field_returns_error(url.put, 'name', None)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'name', 42)
    s.check_bogus_field_returns_error(url, 'name', 'a' * 80)
    s.check_bogus_field_returns_error(url, 'name', 'global')
    s.check_bogus_field_returns_error(url, 'name', 'system')
    s.check_bogus_field_returns_error(url, 'transport', {'uuid': FAKE_UUID})
    s.check_bogus_field_returns_error(
        url, 'aor_section_options', [['one', 'two', 'three']]
    )
    sections = [
        ('aor_section_options', [['auth_type', 'invalid-key']]),
        ('auth_section_options', [['max_contacts', 'invalid-key']]),
        ('auth_section_options', [['@custom_variable', 'invalid-key']]),
        ('endpoint_section_options', [['auth_type', 'invalid-key']]),
        ('identify_section_options', [['auth_type', 'invalid-key']]),
        ('identify_section_options', [['@custom_variable', 'invalid-key']]),
        ('registration_section_options', [['auth_type', 'invalid-key']]),
        ('registration_section_options', [['@custom_variable', 'invalid-key']]),
        (
            'registration_outbound_auth_section_options',
            [['max_contacts', 'invalid-key']],
        ),
        (
            'registration_outbound_auth_section_options',
            [['@custom_variable', 'invalid-key']],
        ),
        ('outbound_auth_section_options', [['max_contacts', 'invalid-key']]),
        ('outbound_auth_section_options', [['@custom_variable', 'invalid-key']]),
    ]
    for section, values in sections:
        s.check_bogus_field_returns_error(url, section, values)

    unique_error_checks(url)


@fixtures.transport(name='transport_unique')
@fixtures.sip(name='endpoint_unique')
@fixtures.sip_template(name='template_unique')
def unique_error_checks(url, transport, sip, template):
    s.check_bogus_field_returns_error(url, 'name', transport['name'])
    s.check_bogus_field_returns_error(url, 'name', template['name'])
    s.check_bogus_field_returns_error(url, 'name', sip['name'])


@fixtures.sip_template()
def test_put_templates_itself(sip):
    result = confd.endpoints.sip.templates(sip['uuid']).put(templates=[sip])
    result.assert_match(400, re.compile(re.escape('itself')))


@fixtures.sip_template()
@fixtures.sip_template()
def test_put_templates_loop(template1, template2):
    body = {'templates': [template2]}
    confd.endpoints.sip.templates(template1['uuid']).put(body).assert_updated()

    body = {'templates': [template1]}
    result = confd.endpoints.sip.templates(template2['uuid']).put(body)
    result.assert_match(400, re.compile(re.escape(template1['uuid'])))


@fixtures.sip_template(name='hidden', label='hidden', asterisk_id='hidden')
@fixtures.sip_template(name='search', label='search', asterisk_id='search')
def test_search(hidden, sip):
    url = confd.endpoints.sip.templates
    searches = {'name': 'search', 'label': 'search', 'asterisk_id': 'search'}

    for field, term in searches.items():
        check_search(url, sip, hidden, field, term)


def check_search(url, template, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, template[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: template[field]})
    assert_that(response.items, has_item(has_entry('uuid', template['uuid'])))
    assert_that(response.items, is_not(has_item(has_entry('uuid', hidden['uuid']))))


@fixtures.sip_template()
@fixtures.sip_template()
def test_list(template1, template2):
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


@fixtures.sip_template(wazo_tenant=MAIN_TENANT)
@fixtures.sip_template(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.endpoints.sip.templates.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_items(main)), not_(has_items(sub)))

    response = confd.endpoints.sip.templates.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_items(sub), not_(has_items(main))))

    response = confd.endpoints.sip.templates.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.sip_template(name='sort1', label='sort1')
@fixtures.sip_template(name='sort2', label='sort2')
def test_sorting_offset_limit(sip1, sip2):
    url = confd.endpoints.sip.templates.get
    s.check_sorting(url, sip1, sip2, 'name', 'sort', 'uuid')
    s.check_sorting(url, sip1, sip2, 'label', 'sort', 'uuid')

    s.check_offset(url, sip1, sip2, 'name', 'sort', 'uuid')
    s.check_limit(url, sip1, sip2, 'name', 'sort', 'uuid')


@fixtures.sip()
@fixtures.sip()
def test_list_db_requests(*_):
    expected_request_count = 1 + 1  # 1 list + 1 count
    s.check_db_requests(
        BaseIntegrationTest,
        confd.endpoints.sip.templates.get,
        nb_requests=expected_request_count,
    )


@fixtures.sip_template()
@fixtures.sip()
def test_get(template, sip):
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
            transport=None,
            asterisk_id=None,
        ),
    )

    response = confd.endpoints.sip.templates(sip['uuid']).get()
    response.assert_match(404, e.not_found())


@fixtures.sip_template(wazo_tenant=MAIN_TENANT)
@fixtures.sip_template(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.endpoints.sip.templates(main['uuid']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='SIPEndpointTemplate'))

    response = confd.endpoints.sip.templates(sub['uuid']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
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


@fixtures.transport()
@fixtures.sip_template()
@fixtures.sip_template()
def test_create_all_parameters(transport, endpoint_1, endpoint_2):
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
    response = confd.endpoints.sip.templates.post(
        name="template_name",
        label="label",
        aor_section_options=aor_section_options,
        auth_section_options=auth_section_options,
        endpoint_section_options=endpoint_section_options,
        identify_section_options=identify_section_options,
        registration_section_options=registration_section_options,
        registration_outbound_auth_section_options=registration_outbound_auth_section_options,
        outbound_auth_section_options=outbound_auth_section_options,
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
            aor_section_options=aor_section_options,
            auth_section_options=auth_section_options,
            endpoint_section_options=endpoint_section_options,
            identify_section_options=identify_section_options,
            registration_section_options=registration_section_options,
            registration_outbound_auth_section_options=registration_outbound_auth_section_options,
            outbound_auth_section_options=outbound_auth_section_options,
            transport=has_entries(uuid=transport['uuid']),
            templates=contains(
                has_entries(uuid=endpoint_1['uuid'], label=endpoint_1['label']),
                has_entries(uuid=endpoint_2['uuid'], label=endpoint_2['label']),
            ),
            asterisk_id='asterisk_id',
        ),
    )


def test_create_multi_tenant():
    response = confd.endpoints.sip.templates.post(wazo_tenant=SUB_TENANT)
    response.assert_created()

    assert_that(response.item, has_entries(tenant_uuid=SUB_TENANT))


@fixtures.sip()
@fixtures.sip_template()
def test_edit_minimal_parameters(sip, template):
    response = confd.endpoints.sip.templates(template['uuid']).put()
    response.assert_updated()

    response = confd.endpoints.sip.templates(sip['uuid']).put()
    response.assert_match(404, e.not_found())


@fixtures.transport()
@fixtures.sip_template()
@fixtures.sip_template(
    aor_section_options=[
        ['@custom_variable', 'custom'],
        ['qualify_frequency', '60'],
        ['maximum_expiration', '3600'],
        ['remove_existing', 'yes'],
        ['max_contacts', '1'],
    ],
    auth_section_options=[['username', 'yiq8yej0'], ['password', 'yagq7x0w']],
    endpoint_section_options=[
        ['@custom_variable', 'custom'],
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
)
def test_edit_all_parameters(transport, template, sip):
    aor = [
        ['maximum_expiration', '3600'],
        ['remove_existing', 'yes'],
        ['max_contacts', '1'],
    ]
    auth = [['username', 'yiq8yej0'], ['password', '1337']]
    endpoint = [
        ['force_rport', 'no'],
        ['rewrite_contact', 'yes'],
        ['callerid', '"Firstname Lastname" <666>'],
    ]
    identify = [
        ['match', '54.172.60.0'],
        ['match', '54.172.60.1'],
        ['match', '54.172.60.2'],
        ['match', '54.172.60.3'],
    ]
    registration = [
        ['client_uri', 'sip:peer@proxy.example.com'],
        ['server_uri', 'sip:proxy.example.com'],
        ['expiration', '90'],
    ]
    registration_outbound_auth = [
        ['username', 'outbound-registration-username'],
        ['password', 'outbound-registration-password'],
    ]
    outbound_auth = [
        ['username', 'outbound-auth'],
        ['password', 'outbound-password'],
    ]
    response = confd.endpoints.sip.templates(sip['uuid']).put(
        aor_section_options=aor,
        auth_section_options=auth,
        endpoint_section_options=endpoint,
        identify_section_options=identify,
        registration_section_options=registration,
        registration_outbound_auth_section_options=registration_outbound_auth,
        outbound_auth_section_options=outbound_auth,
        templates=[template],
        transport=transport,
    )
    response.assert_updated()

    response = confd.endpoints.sip.templates(sip['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            aor_section_options=contains_inanyorder(*aor),
            auth_section_options=contains_inanyorder(*auth),
            endpoint_section_options=contains_inanyorder(*endpoint),
            identify_section_options=contains_inanyorder(*identify),
            registration_section_options=contains_inanyorder(*registration),
            registration_outbound_auth_section_options=contains_inanyorder(
                *registration_outbound_auth
            ),
            outbound_auth_section_options=contains_inanyorder(*outbound_auth),
            templates=contains_inanyorder(
                has_entries(uuid=template['uuid'], label=template['label'])
            ),
            transport=has_entries(uuid=transport['uuid']),
        ),
    )


@fixtures.sip_template(wazo_tenant=MAIN_TENANT)
@fixtures.sip_template(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.endpoints.sip.templates(main['uuid']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='SIPEndpointTemplate'))

    response = confd.endpoints.sip.templates(sub['uuid']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.sip_template()
@fixtures.sip()
def test_edit_template(template, sip):
    response = confd.endpoints.sip.templates(template['uuid']).put()
    response.assert_updated()

    response = confd.endpoints.sip.templates(sip['uuid']).put()
    response.assert_match(404, e.not_found())


@fixtures.sip()
@fixtures.sip_template()
def test_delete(sip, template):
    response = confd.endpoints.sip.templates(template['uuid']).delete()
    response.assert_deleted()

    response = confd.endpoints.sip.templates(sip['uuid']).delete()
    response.assert_match(404, e.not_found())


@fixtures.sip_template(wazo_tenant=MAIN_TENANT)
@fixtures.sip_template(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.endpoints.sip.templates(main['uuid']).delete(
        wazo_tenant=SUB_TENANT
    )
    response.assert_match(404, e.not_found(resource='SIPEndpointTemplate'))

    response = confd.endpoints.sip.templates(sub['uuid']).delete(
        wazo_tenant=MAIN_TENANT
    )
    response.assert_deleted()


@fixtures.sip_template()
@fixtures.sip()
def test_delete_template(template, sip):
    response = confd.endpoints.sip.templates(template['uuid']).delete()
    response.assert_deleted()

    response = confd.endpoints.sip.templates(sip['uuid']).delete()
    response.assert_match(404, e.not_found())


@fixtures.sip_template()
def test_bus_events(sip):
    headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event(
        'sip_endpoint_template_created', headers, confd.endpoints.sip.templates.post
    )
    s.check_event(
        'sip_endpoint_template_edited',
        headers,
        confd.endpoints.sip.templates(sip['uuid']).put,
    )
    s.check_event(
        'sip_endpoint_template_deleted',
        headers,
        confd.endpoints.sip.templates(sip['uuid']).delete,
    )
