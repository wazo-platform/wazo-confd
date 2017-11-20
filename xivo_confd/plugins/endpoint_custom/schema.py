# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields
from marshmallow.validate import Regexp

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean

INTERFACE_REGEX = r"^[a-zA-Z0-9#*./_@:-]{1,128}$"


class CustomSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    interface = fields.String(validate=Regexp(INTERFACE_REGEX), required=True)
    enabled = StrictBoolean()
    links = ListLink(Link('endpoint_custom'))

    trunk = fields.Nested('TrunkSchema', only=['id', 'links'], dump_only=True)
    line = fields.Nested('LineSchema', only=['id', 'links'], dump_only=True)
