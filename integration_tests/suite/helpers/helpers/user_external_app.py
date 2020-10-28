# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from . import (
    confd,
    user as user_helper,
)


def generate_user_external_app(**parameters):
    user_uuid = parameters.pop('user_uuid', None)
    if not user_uuid:
        user = user_helper.generate_user(**parameters)
        user_uuid = user['uuid']
    external_app = add_user_external_app(user_uuid=user_uuid, **parameters)
    external_app['user_uuid'] = user_uuid
    return external_app


def add_user_external_app(user_uuid=None, wazo_tenant=None, **parameters):
    name = parameters.pop('name', generate_name(user_uuid))
    response = (
        confd.users(user_uuid)
        .external.apps(name)
        .post(parameters, wazo_tenant=wazo_tenant)
    )
    return response.item


def delete_user_external_app(user_uuid, name, check=False):
    response = confd.users(user_uuid).external.apps(name).delete()
    if check:
        response.assert_ok()
    user_helper.delete_user(user_uuid, check=False)


def generate_name(user_uuid):
    response = confd.users(user_uuid).external.apps.get()
    names = set(d['name'] for d in response.items)
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in names:
        return _random_name(names)
    return name
