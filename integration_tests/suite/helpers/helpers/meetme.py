# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random
import string

from . import db


def generate_conference(**parameters):
    parameters.setdefault('name', generate_name())
    return add_conference(**parameters)


def add_conference(**parameters):
    with db.queries() as queries:
        id_ = queries.insert_conference_only(**parameters)
    parameters['id'] = id_
    return parameters


def delete_conference(conference_id, check=False):
    with db.queries() as queries:
        queries.delete_conference(conference_id)


def generate_name():
    with db.queries() as queries:
        response = queries.get_conferences()
    names = set(d['name'] for d in response)
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in names:
        return _random_name(names)
    return name
