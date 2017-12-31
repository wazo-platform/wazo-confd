# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields
from marshmallow.validate import Regexp

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.validator import EXTEN_REGEX


class ExtensionFeatureSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    exten = fields.String(validate=Regexp(EXTEN_REGEX), required=True)
    context = fields.String(dump_only=True)
    feature = fields.String(attribute='typeval', dump_only=True)
    enabled = fields.Boolean()
    links = ListLink(Link('extensions_features'))
