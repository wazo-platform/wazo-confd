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
