# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import socket

from marshmallow import fields, post_load, pre_dump, validates_schema
from marshmallow.exceptions import ValidationError

from wazo_confd.helpers.mallow import BaseSchema


class DHCPSchema(BaseSchema):

    active = fields.Boolean(required=True)
    pool_start = fields.String()
    pool_end = fields.String()
    network_interfaces = fields.List(fields.String(), missing=list)

    @validates_schema
    def check_pool_if_active(self, data):
        if not data['active']:
            return

        if 'pool_start' not in data:
            raise ValidationError('missing key: pool_start')
        if 'pool_end' not in data:
            raise ValidationError('missing key: pool_end')

        try:
            ip_start = socket.inet_aton(data['pool_start'])
        except socket.error:
            raise ValidationError(
                'pool_start: invalid IP address: {}'.format(data['pool_start'])
            )
        try:
            ip_end = socket.inet_aton(data['pool_end'])
        except socket.error:
            raise ValidationError(
                'pool_end: invalid IP address: {}'.format(data['pool_end'])
            )

        if ip_end < ip_start:
            raise ValidationError('pool_start must be less than pool_end')

    @pre_dump
    def from_db_model(self, data):
        result = {
            'active': bool(data.active),
            'pool_start': data.pool_start,
            'pool_end': data.pool_end,
            'network_interfaces': [],
        }
        if data.network_interfaces:
            result['network_interfaces'] = data.network_interfaces.split(',')
        return result

    @post_load
    def to_db_model(self, data):
        data['active'] = int(data['active'])
        data['network_interfaces'] = ','.join(data['network_interfaces'])
        return data
