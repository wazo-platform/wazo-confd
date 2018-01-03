# -*- coding: UTF-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields
from marshmallow.validate import Length, Regexp, OneOf

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink

NAME_REGEX = r"^[a-zA-Z0-9_-]{1,40}$"


class IAXSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Regexp(NAME_REGEX))
    type = fields.String(validate=OneOf(['friend', 'peer', 'user']))
    host = fields.String(validate=Length(max=255))
    options = fields.List(fields.List(fields.String(), validate=Length(equal=2)))
    links = ListLink(Link('endpoint_iax'))

    # trunk = fields.Nested('TrunkSchema', only=['id', 'links'], dump_only=True)
