# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    greater_than,
    has_entries,
    starts_with,
)
from wazo_test_helpers.hamcrest.uuid_ import uuid_

from . import BaseIntegrationTest, confd
from ..helpers import config, fixtures

FULL_USER = {
    "firstname": "Jôhn",
    "lastname": "Smêth",
}

NULL_USER = {
    "firstname": "Jôhn",
    "lastname": None,
}

ALL_NULL_USER = {
    "firstname": None,
    "lastname": None,
}


def test_post_basic_user_no_error():
    response = confd.users.post({'user': {'firstname': 'Jôhn'}}).response
    assert response.status_code == 201

    assert_that(
        response.json(),
        has_entries(
            user=has_entries(
                id=greater_than(0),
                uuid=uuid_(),
                firstname='Jôhn',
            ),
        ),
    )


def test_post_user_missing_field_return_error():
    response = confd.users.post({'user': {'lastname': 'Jôhn'}}).response
    assert response.status_code == 400
    assert_that(
        response.json(),
        has_entries(
            details=has_entries(
                user=has_entries(
                    firstname=has_entries(
                        constraint_id='required',
                    )
                )
            )
        ),
    )


def test_post_user_wrong_type_return_error():
    user = {"firstname": "Rîchard", "enabled": "True"}
    response = confd.users.post({'user': user}).response
    assert response.status_code == 400
    assert_that(
        response.json(),
        has_entries(
            details=has_entries(
                user=has_entries(
                    enabled=has_entries(
                        constraint_id='type',
                        constraint='boolean',
                    )
                )
            )
        ),
    )


@fixtures.transport()
@fixtures.sip_template()
@fixtures.registrar()
def test_post_full_user_no_error(transport, template, registrar):
    user = {
        "subscription_type": 2,
        "firstname": "Rîchard",
        "lastname": "Lâpointe",
        "email": "richard@lapointe.org",
        "language": "fr_FR",
        "outgoing_caller_id": '"Rîchy Cool" <4185551234>',
        "mobile_phone_number": "4181234567",
        "supervision_enabled": True,
        "call_transfer_enabled": False,
        "dtmf_hangup_enabled": True,
        "call_record_outgoing_external_enabled": True,
        "call_record_outgoing_internal_enabled": True,
        "call_record_incoming_internal_enabled": True,
        "call_record_incoming_external_enabled": True,
        "online_call_record_enabled": False,
        "simultaneous_calls": 5,
        "ring_seconds": 30,
        "userfield": "userfield",
        "call_permission_password": "1234",
        "enabled": True,
        "username": "richardlapointe",
        "password": "secret",
    }
    extension = {'context': config.CONTEXT, 'exten': '1001'}
    line = {
        'context': config.CONTEXT,
        'position': 2,
        'registrar': registrar['id'],
        'provisioning_code': "887865",
        'extensions': [extension],
        'endpoint_sip': {
            'name': 'iddqd',
            'label': 'Richard\'s line',
            'auth_section_options': [
                ['username', 'iddqd'],
                ['password', 'secret'],
            ],
            'endpoint_section_options': [
                ['callerid', '"Rîchard Lâpointe" <1001>'],
            ],
            'transport': transport,
            'templates': [template],
        },
    }

    response = confd.users.post(
        {
            'lines': [line],
            **user,
        }
    ).response

    assert response.status_code == 201
    payload = response.json()
    try:
        assert_that(
            payload,
            has_entries(
                uuid=uuid_(),
                lines=contains(
                    has_entries(
                        id=greater_than(0),
                        endpoint_sip=has_entries(uuid=uuid_()),
                        extensions=contains(has_entries(id=greater_than(0))),
                    )
                ),
                **user,
            ),
        )

        assert_that(
            confd.users(payload['uuid']).get().item,
            has_entries(lines=contains(has_entries(id=payload['lines'][0]['id']))),
        )

        assert_that(
            confd.lines(payload['lines'][0]['id']).get().item,
            has_entries(
                extensions=contains(has_entries(**extension)),
                endpoint_sip=has_entries(name='iddqd'),
            )
        )
    finally:
        confd.users(payload['uuid']).delete().assert_deleted()
        confd.lines(payload['lines'][0]['id']).delete().assert_deleted()
        confd.extensions(payload['lines'][0]['extensions'][0]['id']).delete().assert_deleted()


def test_duplicated_email():
    user = {
        "subscription_type": 2,
        "firstname": "Rîchard",
        "lastname": "Lâpointe",
        "email": "richard@lapointe.org",
    }

    user_1_response = confd.users.post({'user': user})

    try:
        user_2_response = confd.users.post({'user': user})
        assert user_2_response.response.status_code == 400
        assert_that(
            user_2_response.response.json(),
            has_entries(
                message="Resource Error - User already exists ('email': 'richard@lapointe.org')"
            ),
        )
    finally:
        confd.users(user_1_response.item['user']['id']).delete()


@fixtures.transport()
@fixtures.sip_template()
@fixtures.registrar()
def test_stopped_provd(transport, template, registrar):
    user = {
        "subscription_type": 2,
        "firstname": "Rîchard",
        "lastname": "Lâpointe",
        "email": "richard@lapointe.org",
    }
    extension = {'context': config.CONTEXT, 'exten': '1001'}
    line = {
        # 'context': config.CONTEXT,  # We will use the context from the extension
        'position': 2,
        'registrar': registrar['id'],
        'provisioning_code': "887865",
        'extensions': [extension],
        'endpoint_sip': {
            'name': 'iddqd',
            'label': 'Richard\'s line',
            'auth_section_options': [
                ['username', 'iddqd'],
                ['password', 'secret'],
            ],
            'endpoint_section_options': [
                ['callerid', '"Rîchard Lâpointe" <1001>'],
            ],
            'transport': transport,
            'templates': [template],
        },
    }

    BaseIntegrationTest.stop_service('provd')
    try:
        response = confd.users.post({'user': user, 'lines': [line]}).response
        assert response.status_code == 500
        assert_that(
            response.json(),
            has_entries(
                error_id='unexpected',
                message=starts_with('Unexpected error'),
            ),
        )
    finally:
        BaseIntegrationTest.start_service('provd')
