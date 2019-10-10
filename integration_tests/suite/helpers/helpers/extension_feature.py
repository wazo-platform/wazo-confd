# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random

from . import confd, db


def generate_extension_feature(**parameters):
    parameters.setdefault('exten', generate_exten())
    parameters.setdefault('feature', 'generated_feature')
    return add_extension_feature(**parameters)


def add_extension_feature(**parameters):
    with db.queries() as queries:
        id = queries.insert_extension_feature(**parameters)
    return {
        'id': id,
        'exten': parameters.get('exten'),
        'context': 'xivo-features',
        'feature': parameters.get('feature'),
    }


def delete_extension_feature(extension_feature_id, check=False):
    with db.queries() as queries:
        queries.delete_extension_feature(extension_feature_id)


def generate_exten():
    response = confd.extensions.features.get()
    extens = set(d['exten'] for d in response.items)
    return _random_exten(extens)


def _random_exten(extens):
    exten = ''.join(random.choice('1234567890') for _ in range(5))
    if exten in extens:
        return _random_exten(extens)
    return exten
