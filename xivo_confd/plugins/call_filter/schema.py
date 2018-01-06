# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields
from marshmallow.validate import OneOf, Length, Range

from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink


class CallFilterSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=128), required=True)
    mode = fields.String(validate=OneOf([
        'bossfirst-serial',
        'bossfirst-simult',
        'secretary-serial',
        'secretary-simult',
        'all',
    ]), required=True)
    from_ = fields.String(validate=OneOf([
        'internal',
        'external',
        'all',
    ]), attribute='callfrom', required=True)
    caller_id_mode = fields.String(validate=OneOf([
        'prepend',
        'overwrite',
        'append',
    ]), allow_none=True)
    caller_id_name = fields.String(validate=Length(max=80), allow_none=True)
    timeout = fields.Integer(validate=Range(min=0), allow_none=True)
    description = fields.String(allow_none=True)
    enabled = StrictBoolean()
    links = ListLink(Link('callfilters'))
