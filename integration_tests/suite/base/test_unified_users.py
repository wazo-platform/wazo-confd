# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from . import confd

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
    response = confd.unified_users.post({'user': {'firstname': 'Jôhn'}}).response
    assert response.status_code == 201

    returned_json = response.json()
    assert 'user' in returned_json

    created_user = returned_json['user']
    assert created_user['firstname'] == 'Jôhn'
    assert 'id' in created_user and created_user['id']
    assert 'uuid' in created_user and created_user['uuid']


def test_post_user_missing_field_return_error():
    response = confd.unified_users.post({'user': {'lastname': 'Jôhn'}}).response
    assert response.status_code == 400
    assert (
        response.json()['details']['user']['firstname']['constraint_id'] == 'required'
    )


def test_post_user_wrong_type_return_error():
    user = {"firstname": "Rîchard", "enabled": "True"}
    response = confd.unified_users.post({'user': user}).response
    assert response.status_code == 400
    assert (
        response.json()['details']['user']['enabled']['constraint_id'] == 'type'
        and response.json()['details']['user']['enabled']['constraint'] == 'boolean'
    )


def test_post_full_user_no_error():
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
    response = confd.unified_users.post({'user': user}).response

    assert response.status_code == 201

    returned_json = response.json()

    assert 'user' in returned_json

    created_user = returned_json['user']

    assert_that(created_user, has_entries(user))
    assert 'uuid' in created_user and created_user['uuid']
