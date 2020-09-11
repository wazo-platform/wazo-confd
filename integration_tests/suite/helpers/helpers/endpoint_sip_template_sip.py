# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def associate(sip_uuid, templates, check=True):
    response = confd.endpoints.sip(sip_uuid).put(templates=templates)
    if check:
        response.assert_ok()


def dissociate(sip_uuid, check=True):
    response = confd.endpoints.sip(sip_uuid).put(templates=[])
    if check:
        response.assert_ok()
