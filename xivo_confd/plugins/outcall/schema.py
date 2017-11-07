# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+


from marshmallow import fields, post_dump
from marshmallow.validate import Length, Range

from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink


class OutcallSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=128), required=True)
    internal_caller_id = StrictBoolean()
    preprocess_subroutine = fields.String(validate=Length(max=39))
    ring_time = fields.Integer(validate=Range(min=0), allow_none=True)
    description = fields.String(allow_none=True)
    enabled = StrictBoolean()
    links = ListLink(Link('outcalls'))
    trunks = fields.Nested('TrunkSchema',
                           only=['id', 'endpoint_sip', 'endpoint_custom', 'links'],
                           many=True,
                           dump_only=True)
    extensions = fields.Nested('DialPatternSchema',
                               attribute='dialpatterns',
                               many=True,
                               dump_only=True)


class DialPatternSchema(BaseSchema):
    external_prefix = fields.String()
    prefix = fields.String()
    strip_digits = fields.Integer()
    caller_id = fields.String()
    extension = fields.Nested('ExtensionSchema',
                              only=['id', 'exten', 'context', 'links'])

    @post_dump(pass_many=True)
    def merge_extension_dialpattern(self, data, many):
        if not many:
            return self.merge_extension(data)

        for row in data:
            row = self._merge_extension(row)
        return data

    def _merge_extension(self, row):
        extension = row.pop('extension', None)
        row['id'] = extension.get('id', None)
        row['exten'] = extension.get('exten', None)
        row['context'] = extension.get('context', None)
        row['links'] = extension.get('links', [])
        return row
