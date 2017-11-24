# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random
import string

from . import db
from . import confd


def generate_cti_profile(**parameters):
    parameters.setdefault('name', generate_name())
    return add_cti_profile(**parameters)


def add_cti_profile(**parameters):
    with db.queries() as queries:
        id = queries.insert_cti_profile(**parameters)
    parameters['id'] = id
    return parameters


def delete_cti_profile(cti_profile_id, check=False):
    with db.queries() as queries:
        queries.dissociate_cti_profile(cti_profile_id)
        queries.delete_cti_profile(cti_profile_id)


def generate_name():
    response = confd.cti_profiles.get()
    names = set(d['name'] for d in response.items)
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in names:
        return _random_name(names)
    return name
