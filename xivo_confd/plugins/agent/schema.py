# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields
from marshmallow.validate import Length

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink


class AgentSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    number = fields.String(validate=Length(max=40), required=True)  # TODO validate with a REGEX
    firstname = fields.String(validate=Length(max=128), allow_none=True)
    lastname = fields.String(validate=Length(max=128), allow_none=True)
    password = fields.String(validate=Length(max=128), allow_none=True, attribute='passwd')
    language = fields.String(validate=Length(max=20), allow_none=True)
    preprocess_subroutine = fields.String(validate=Length(max=39), allow_none=True)
    description = fields.String(allow_none=True)
    links = ListLink(Link('agents'))


# TODO cannot editing number
