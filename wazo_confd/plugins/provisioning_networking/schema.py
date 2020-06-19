# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from wazo_confd.helpers.mallow import BaseSchema


class ProvisioningNetworkingSchema(BaseSchema):

    provision_host = fields.String(attribute='net4_ip', allow_none=True)
    provision_http_port = fields.Integer(attribute='http_port')
