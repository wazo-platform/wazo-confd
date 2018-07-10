# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields
from marshmallow.validate import Length

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink


class SkillSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=64), required=True)
    category = fields.String(validate=Length(max=64), allow_none=True)
    description = fields.String(allow_none=True)
    links = ListLink(Link('skills'))
