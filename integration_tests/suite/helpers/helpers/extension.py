# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from ..config import CONTEXT, EXTEN_USER_RANGE
from . import confd


def generate_extension(**parameters):
    exten_range = parameters.pop('exten_range', EXTEN_USER_RANGE)
    parameters.setdefault('context', CONTEXT)
    parameters.setdefault(
        'exten',
        find_available_exten(parameters['context'], exten_range),
    )
    return add_extension(**parameters)


def find_available_exten(context, exten_range=EXTEN_USER_RANGE, exclude=None):
    exclude = {int(n) for n in exclude} if exclude else set()
    response = confd.extensions.get(context=context, recurse=True)
    numbers = [int(e['exten']) for e in response.items if e['exten'].isdigit()]

    available = set(exten_range) - set(numbers) - exclude
    return str(available.pop())


def add_extension(wazo_tenant=None, **params):
    response = confd.extensions.post(params, wazo_tenant=wazo_tenant)
    return response.item


def delete_extension(extension_id, check=False, **params):
    response = confd.extensions(extension_id).delete()
    if check:
        response.assert_ok()
