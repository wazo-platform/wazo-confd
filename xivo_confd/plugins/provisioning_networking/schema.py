# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import socket

from marshmallow import fields, post_load, validates
from marshmallow.exceptions import ValidationError

from xivo_confd.helpers.mallow import BaseSchema


class ProvisioningNetworkingSchema(BaseSchema):

    provision_ip = fields.String(attribute='net4_ip')
    provision_http_port = fields.Integer(attribute='http_port')
    rest_ip = fields.String(attribute='net4_ip_rest')
    rest_https_port = fields.Integer(attribute='rest_port')
    dhcp_integration = fields.Boolean(attribute='dhcp_integration')

    def _check_ip(self, field_name, ip):
        try:
            _ = socket.inet_aton(ip)
        except socket.error:
            raise ValidationError('{}: invalid IP address: {}'.format(field_name, ip))

    @validates('provision_ip')
    def check_provision_ip(self, value):
        self._check_ip('provision_ip', value)

    @validates('rest_ip')
    def check_rest_ip(self, value):
        self._check_ip('rest_ip', value)

    @post_load
    def to_db_model(self, data):
        if 'dhcp_integration' in data:
            data['dhcp_integration'] = int(data['dhcp_integration'])
        return data
