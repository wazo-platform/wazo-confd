# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd
from .. import config


def generate_extension(**parameters):
    parameters.setdefault('context', config.CONTEXT)
    if 'exten' not in parameters:
        parameters['exten'] = find_available_exten(parameters['context'])
    return add_extension(**parameters)


def find_available_exten(context, exclude=None):
    exclude = {int(n) for n in exclude} if exclude else set()
    response = confd.extensions.get()
    numbers = [int(e['exten'])
               for e in response.items
               if e['context'] == context and e['exten'].isdigit()]

    available = set(config.EXTENSION_RANGE) - set(numbers) - exclude
    return str(available.pop())


def add_extension(**params):
    response = confd.extensions.post(params)
    return response.item


def delete_extension(extension_id, check=False):
    response = confd.extensions(extension_id).delete()
    if check:
        response.assert_ok()
