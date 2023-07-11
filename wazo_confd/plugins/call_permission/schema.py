# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from marshmallow import fields, pre_load
from marshmallow.validate import Length, OneOf, Regexp

from wazo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink, Nested

PASSWORD_REGEX = r'^[0-9#\*]{1,40}$'
EXTENSION_REGEX = r'^(?:_?\+?[0-9NXZ\*#\-\[\]]+[\.\!]?){1,40}$'

logger = logging.getLogger(__name__)


class CallPermissionSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(dump_only=True)
    label = fields.String(validate=Length(min=1, max=128), required=True)
    password = fields.String(validate=Regexp(PASSWORD_REGEX), allow_none=True)
    mode = fields.String(validate=OneOf(['allow', 'deny']))
    extensions = fields.List(fields.String(validate=Regexp(EXTENSION_REGEX)))
    enabled = StrictBoolean()
    description = fields.String(allow_none=True)
    links = ListLink(Link('callpermissions'))

    outcalls = Nested(
        'OutcallSchema', only=['id', 'name', 'links'], many=True, dump_only=True
    )
    groups = Nested(
        'GroupSchema', only=['uuid', 'id', 'name', 'links'], many=True, dump_only=True
    )
    users = Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname', 'links'],
        many=True,
        dump_only=True,
    )

    # DEPRECATED 23.10
    @pre_load
    def copy_name_to_label(self, data, **kwargs):
        if 'label' in data:
            return data
        if 'name' in data:
            logger.warning(
                'The "name" field of call_permission is deprecated. Use "label" instead'
            )
            data['label'] = data['name']
        return data
