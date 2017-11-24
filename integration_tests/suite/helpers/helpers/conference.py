# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def generate_conference(**parameters):
    return add_conference(**parameters)


def add_conference(**parameters):
    response = confd.conferences.post(parameters)
    return response.item


def delete_conference(conference_id, check=False):
    response = confd.conferences(conference_id).delete()
    if check:
        response.assert_ok()
