# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from . import confd


def generate_user_blocklist_number(confd_client=confd, **parameters):
    parameters.setdefault('number', _random_number(10))
    return add_user_blocklist_number(confd_client=confd_client, **parameters)


def delete_user_blocklist_number(
    blocklist_number_uuid, confd_client=confd, check=False, **parameters
):
    response = confd_client.users.me.blocklist.numbers(blocklist_number_uuid).delete()
    if check:
        response.assert_ok()


def add_user_blocklist_number(confd_client=confd, wazo_tenant=None, **parameters):
    response = confd_client.users.me.blocklist.numbers.post(
        parameters, wazo_tenant=wazo_tenant
    )
    return confd_client.users.me.blocklist.numbers(response.item['uuid']).get().item


def _random_number(length):
    number = ''.join(random.choice(string.digits) for _ in range(length))
    return f'+{number}'
