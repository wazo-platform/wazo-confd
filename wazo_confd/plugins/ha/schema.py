# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, validates_schema
from marshmallow.exceptions import ValidationError
from marshmallow.validate import OneOf

from wazo_confd.helpers.mallow import BaseSchema


class HASchema(BaseSchema):

    node_type = fields.String(validate=OneOf(['disabled', 'master', 'slave']), required=True)
    remote_address = fields.String(missing='')

    @validates_schema
    def check_remote_if_enabled(self, data):
        if 'node_type' not in data:
            return
        if data['node_type'] == 'disabled':
            return

        if not data['remote_address']:
            raise ValidationError('remote_address cannot be empty')
