# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
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
from ..helpers import errors as e, fixtures, scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT


FAKE_UUID = '99999999-9999-4999-9999-999999999999'


def test_get_errors():
    fake_sip_get = confd.endpoints.sip(FAKE_UUID).get
    yield s.check_resource_not_found, fake_sip_get, 'SIPEndpoint'


def test_post_errors():
    url = confd.endpoints.sip.post
    for check in error_checks(url):
        yield check


@fixtures.sip()
def test_put_errors(sip):
    url = confd.endpoints.sip(sip['uuid']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 42
    yield s.check_bogus_field_returns_error, url, 'name', 'a' * 129
    # TODO(pc-m): add check for fields in the right section


@fixtures.sip()
def test_delete_errors(sip):
    url = confd.endpoints.sip(sip['uuid'])
    url.delete()
    yield s.check_resource_not_found, url.get, 'SIPEndpoint'


@fixtures.sip(wazo_tenant=MAIN_TENANT)
@fixtures.sip(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.endpoints.sip.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_items(main)), not_(has_items(sub)))

    response = confd.endpoints.sip.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_items(sub), not_(has_items(main))))

    response = confd.endpoints.sip.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.sip()
def test_get(sip):
    response = confd.endpoints.sip(sip['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            uuid=not_none(),
            name=has_length(8),
            display_name=None,
            aor_section_options=instance_of(list),
            auth_section_options=instance_of(list),
            endpoint_section_options=instance_of(list),
            identify_section_options=instance_of(list),
            registration_section_options=instance_of(list),
            registration_outbound_auth_section_options=instance_of(list),
            outbound_auth_section_options=instance_of(list),
            parents=instance_of(list),
            trunk=None,
            line=None,
            transport=None,
            context=None,
            asterisk_id=None,
        ),
    )


@fixtures.sip()
@fixtures.sip()
def test_list(sip1, sip2):
    response = confd.endpoints.sip.get()
    assert_that(
        response.items,
        has_items(has_entry('uuid', sip1['uuid']), has_entry('uuid', sip2['uuid'])),
    )

    response = confd.endpoints.sip.get(search=sip1['name'])
    assert_that(response.items, contains(has_entry('uuid', sip1['uuid'])))


@fixtures.sip(wazo_tenant=MAIN_TENANT)
@fixtures.sip(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.endpoints.sip(main['uuid']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='SIPEndpoint'))

    response = confd.endpoints.sip(sub['uuid']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.endpoints.sip.post()

    response.assert_created()
    assert_that(
        response.item,
        has_entries(
            uuid=not_none(),
            tenant_uuid=MAIN_TENANT,
            name=not_none(),
            display_name=none(),
            aor_section_options=empty(),
            auth_section_options=empty(),
            endpoint_section_options=empty(),
            identify_section_options=empty(),
            registration_section_options=empty(),
            registration_outbound_auth_section_options=empty(),
            outbound_auth_section_options=empty(),
            parents=empty(),
            asterisk_id=none(),
            template=False,
        ),
    )


@fixtures.context()
@fixtures.transport()
@fixtures.sip()
@fixtures.sip()
def test_create_all_parameters(context, transport, endpoint_1, endpoint_2):
    response = confd.endpoints.sip.post(
        name="name",
        display_name="display_name",
        template=True,
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
        parents=[endpoint_1, endpoint_2],
        asterisk_id='asterisk_id',
    )

    assert_that(
        response.item,
        has_entries(
            tenant_uuid=MAIN_TENANT,
            name='name',
            display_name='display_name',
            template=True,
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
            parents=contains(
                has_entries(uuid=endpoint_1['uuid']),
                has_entries(uuid=endpoint_2['uuid']),
            ),
            asterisk_id='asterisk_id',
        ),
    )


@fixtures.sip(name="dupname")
def test_create_name_already_taken(sip):
    response = confd.endpoints.sip.post(name="dupname")
    response.assert_match(400, e.resource_exists('SIPEndpoint'))


@fixtures.sip()
def test_update_required_parameters(sip):
    url = confd.endpoints.sip(sip['uuid'])

    response = url.put()
    response.assert_updated()

    response = url.get()
    assert_that(
        response.item,
        has_entries(
            uuid=not_none(),
            tenant_uuid=MAIN_TENANT,
            name=not_none(),
            display_name=none(),
            aor_section_options=empty(),
            auth_section_options=empty(),
            endpoint_section_options=empty(),
            identify_section_options=empty(),
            registration_section_options=empty(),
            registration_outbound_auth_section_options=empty(),
            outbound_auth_section_options=empty(),
            parents=empty(),
            asterisk_id=none(),
            template=False,
        ),
    )


@fixtures.sip(
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
    ]
)
def test_update_options(sip):
    url = confd.endpoints.sip(sip['uuid'])
    response = url.put(
        aor_section_options=[
            ['maximum_expiration', '3600'],
            ['remove_existing', 'yes'],
            ['max_contacts', '1'],
        ],
        auth_section_options=[['username', 'yiq8yej0'], ['password', '1337']],
        endpoint_section_options=[
            ['force_rport', 'no'],
            ['rewrite_contact', 'yes'],
            ['callerid', '"Firstname Lastname" <666>'],
        ],
        identify_section_options=[
            ['match', '54.172.60.0'],
            ['match', '54.172.60.1'],
            ['match', '54.172.60.2'],
            ['match', '54.172.60.3'],
        ],
        registration_section_options=[
            ['client_uri', 'sip:peer@proxy.example.com'],
            ['server_uri', 'sip:proxy.example.com'],
            ['expiration', '90'],
        ],
        registration_outbound_auth_section_options=[
            ['username', 'outbound-registration-username'],
            ['password', 'outbound-registration-password'],
        ],
        outbound_auth_section_options=[
            ['username', 'outbound-auth'],
            ['password', 'outbound-password'],
        ]
    )
    response.assert_updated()

    response = url.get()
    assert_that(
        response.item,
        has_entries(
            aor_section_options=contains_inanyorder(
                ['maximum_expiration', '3600'],
                ['remove_existing', 'yes'],
                ['max_contacts', '1'],
            ),
            auth_section_options=contains_inanyorder(['username', 'yiq8yej0'], ['password', '1337']),
            endpoint_section_options=contains_inanyorder(
                ['force_rport', 'no'],
                ['rewrite_contact', 'yes'],
                ['callerid', '"Firstname Lastname" <666>'],
            ),
            identify_section_options=contains_inanyorder(
                ['match', '54.172.60.0'],
                ['match', '54.172.60.1'],
                ['match', '54.172.60.2'],
                ['match', '54.172.60.3'],
            ),
            registration_section_options=contains_inanyorder(
                ['client_uri', 'sip:peer@proxy.example.com'],
                ['server_uri', 'sip:proxy.example.com'],
                ['expiration', '90'],
            ),
            registration_outbound_auth_section_options=contains_inanyorder(
                ['username', 'outbound-registration-username'],
                ['password', 'outbound-registration-password'],
            ),
            outbound_auth_section_options=contains_inanyorder(
                ['username', 'outbound-auth'],
                ['password', 'outbound-password'],
            ),
        ))


@fixtures.sip(wazo_tenant=MAIN_TENANT)
@fixtures.sip(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.endpoints.sip(main['uuid']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='SIPEndpoint'))

    response = confd.endpoints.sip(sub['uuid']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.sip()
def test_delete(sip):
    response = confd.endpoints.sip(sip['uuid']).delete()
    response.assert_deleted()


@fixtures.sip(wazo_tenant=MAIN_TENANT)
@fixtures.sip(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.endpoints.sip(main['uuid']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='SIPEndpoint'))

    response = confd.endpoints.sip(sub['uuid']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()
