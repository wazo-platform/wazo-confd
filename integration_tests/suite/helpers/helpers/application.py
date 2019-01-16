# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def generate_application(**parameters):
    return add_application(**parameters)


def add_application(wazo_tenant=None, **parameters):
    response = confd.applications.post(parameters, wazo_tenant=wazo_tenant)
    return response.item


def delete_application(application_uuid, check=False):
    response = confd.applications(application_uuid).delete()
    if check:
        response.assert_ok()
