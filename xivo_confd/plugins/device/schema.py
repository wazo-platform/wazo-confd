# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Regexp

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean


IP_REGEX = r'(1?\d{1,2}|2([0-4][0-9]|5[0-5]))(\.(1?\d{1,2}|2([0-4][0-9]|5[0-5]))){3}$'
MAC_REGEX = r'^([0-9A-Fa-f]{2})(:[0-9A-Fa-f]{2}){5}$'


class DeviceOptionsSchema(BaseSchema):
    switchboard = StrictBoolean()


class DeviceSchema(BaseSchema):
    id = fields.String(dump_only=True)
    status = fields.String(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    is_new = StrictBoolean(dump_only=True)
    ip = fields.String(validate=Regexp(IP_REGEX), allow_none=True)
    mac = fields.String(validate=Regexp(MAC_REGEX), allow_none=True)
    sn = fields.String(allow_none=True)
    plugin = fields.String(allow_none=True)
    vendor = fields.String(allow_none=True)
    model = fields.String(allow_none=True)
    version = fields.String(allow_none=True)
    description = fields.String(allow_none=True)
    template_id = fields.String(allow_none=True)
    options = fields.Nested(DeviceOptionsSchema, allow_none=True)
    links = ListLink(Link('devices'))
