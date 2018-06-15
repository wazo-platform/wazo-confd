# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields
from marshmallow.validate import Length, Regexp

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink

NUMBER_REGEX = r"^[0-9\*#]{1,40}$"


class AgentSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    number = fields.String(validate=Regexp(NUMBER_REGEX), required=True)
    firstname = fields.String(validate=Length(max=128), allow_none=True)
    lastname = fields.String(validate=Length(max=128), allow_none=True)
    password = fields.String(validate=Length(max=128), allow_none=True, attribute='passwd')
    language = fields.String(validate=Length(max=20), allow_none=True)
    preprocess_subroutine = fields.String(validate=Length(max=39), allow_none=True)
    description = fields.String(allow_none=True)
    links = ListLink(Link('agents'))


class AgentSchemaPUT(AgentSchema):
    number = fields.String(dump_only=True)
