# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from xivo_confd.helpers.mallow import BaseSchema


class ProvisioningNetworkingSchema(BaseSchema):

    provision_host = fields.String(attribute='net4_ip')
    provision_http_port = fields.Integer(attribute='http_port')
    rest_host = fields.String(attribute='net4_ip_rest')
    rest_https_port = fields.Integer(attribute='rest_port')
