# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from marshmallow import fields, post_dump, pre_load
from marshmallow.validate import Length, Range

from wazo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink, Nested

logger = logging.getLogger(__name__)


class OutcallSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(dump_only=True)
    label = fields.String(validate=Length(max=128), required=True)
    internal_caller_id = StrictBoolean()
    preprocess_subroutine = fields.String(validate=Length(max=39), allow_none=True)
    ring_time = fields.Integer(validate=Range(min=0), allow_none=True)
    description = fields.String(allow_none=True)
    enabled = StrictBoolean()
    links = ListLink(Link('outcalls'))
    trunks = Nested(
        'TrunkSchema',
        only=['tenant_uuid', 'id', 'endpoint_sip', 'endpoint_custom', 'links'],
        many=True,
        dump_only=True,
    )
    extensions = Nested(
        'DialPatternSchema', attribute='dialpatterns', many=True, dump_only=True
    )
    schedules = Nested(
        'ScheduleSchema',
        only=['tenant_uuid', 'id', 'name', 'links'],
        many=True,
        dump_only=True,
    )
    call_permissions = Nested(
        'CallPermissionSchema',
        only=['tenant_uuid', 'id', 'name', 'links'],
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
                'The "name" field of outcall is deprecated. Use "label" instead'
            )
            data['label'] = data['name']
        return data


class DialPatternSchema(BaseSchema):
    external_prefix = fields.String()
    prefix = fields.String()
    strip_digits = fields.Integer()
    caller_id = fields.String()
    extension = Nested('ExtensionSchema', only=['id', 'exten', 'context', 'links'])

    @post_dump
    def merge_extension_dialpattern(self, data, **kwargs):
        extension = data.pop('extension', None)
        if not extension:
            return data

        data['id'] = extension.get('id', None)
        data['exten'] = extension.get('exten', None)
        data['context'] = extension.get('context', None)
        data['links'] = extension.get('links', [])
        return data
