# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    has_entries,
)

from . import confd, confd_v2_0
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
    response = confd_v2_0.users.post({'user': {'firstname': 'Jôhn'}}).response
    assert response.status_code == 201

    returned_json = response.json()
    assert 'user' in returned_json

    created_user = returned_json['user']
    assert created_user['firstname'] == 'Jôhn'
    assert 'id' in created_user and created_user['id']
    assert 'uuid' in created_user and created_user['uuid']


def test_post_user_missing_field_return_error():
    response = confd_v2_0.users.post({'user': {'lastname': 'Jôhn'}}).response
    assert response.status_code == 400
    assert (
        response.json()['details']['user']['firstname']['constraint_id'] == 'required'
    )


def test_post_user_wrong_type_return_error():
    user = {"firstname": "Rîchard", "enabled": "True"}
    response = confd_v2_0.users.post({'user': user}).response
    assert response.status_code == 400
    assert (
        response.json()['details']['user']['enabled']['constraint_id'] == 'type'
        and response.json()['details']['user']['enabled']['constraint'] == 'boolean'
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
        # 'context': config.CONTEXT,  # We will use the context from the extension
        'position': 2,
        'registrar': registrar['id'],
        'provisioning_code': "887865",
        'extensions': [extension],
        'endpoint_type': 'sip',
        'endpoint_sip': {
            'name': 'foobar',
            'label': 'Richard\'s line',
            'auth_section_options': [
                ['username', 'foobar'],
                ['password', 'secret'],
            ],
            'endpoint_section_options': [
                ['callerid', '"Rîchard Lâpointe" <1001>'],
            ],
            'transport': transport,
            'templates': [template],
        },
    }

    response = confd_v2_0.users.post({
        'user': user,
        'lines': [line],
    }).response

    assert response.status_code == 201

    returned_json = response.json()

    assert 'user' in returned_json
    assert 'lines' in returned_json

    created_user = returned_json['user']
    created_line = returned_json['lines'][0]
    created_extension = created_line['extensions'][0]
    # created_endpoint_sip = returned_json['lines'][0]['endpoint_sip']

    try:
        assert_that(created_user, has_entries(user))
        assert 'uuid' in created_user and created_user['uuid']

        # TODO(pc-m): removing the endpoint should not be necessary when the association gets implemented
        del line['extensions']
        del line['endpoint_sip']
        del line['endpoint_type']
        assert_that(created_line, has_entries(line))
        assert 'id' in created_line and created_line['id']

        assert_that(created_extension, has_entries(extension))

        # assert_that(created_endpoint_sip, has_entries(line['endpoint_sip']))
        # assert 'uuid' in created_endpoint_sip and created_endpoint_sip['uuid']
    finally:
        confd.users(created_user['id']).delete()
        confd.lines(created_line['id']).delete()
        confd.extensions(created_extension['id']).delete()

