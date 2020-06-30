# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def associate(transport_uuid, endpoint_uuid, check=True):
    response = confd.endpoints.sip(endpoint_uuid).put(
        transport={'uuid': transport_uuid},
    )
    if check:
        response.assert_ok()


def dissociate(transport_uuid, endpoint_uuid, check=True):
    response = confd.endpoints.sip(endpoint_uuid).put(
        transport=None,
    )
    if check:
        response.assert_ok()
