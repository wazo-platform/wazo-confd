# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def generate_application(**parameters):
    return add_application(**parameters)


def add_application(**parameters):
    response = confd.applications.post(parameters)
    return response.item


def delete_application(application_uuid, check=False):
    response = confd.applications(application_uuid).delete()
    if check:
        response.assert_ok()
