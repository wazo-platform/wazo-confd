# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields, post_load
from marshmallow.validate import Length, Range, OneOf

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_confd.helpers.destination import DestinationField
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean


class QueueSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=128), required=True)
    label = fields.String(validate=Length(max=128), missing=None)
    data_quality = StrictBoolean(attribute='data_quality_bool')
    dtmf_hangup_callee_enabled = StrictBoolean()
    dtmf_hangup_caller_enabled = StrictBoolean()
    dtmf_transfer_callee_enabled = StrictBoolean()
    dtmf_transfer_caller_enabled = StrictBoolean()
    dtmf_record_callee_enabled = StrictBoolean()
    dtmf_record_caller_enabled = StrictBoolean()
    retry_on_timeout = StrictBoolean()
    ring_on_hold = StrictBoolean()
    timeout = fields.Integer(validate=Range(min=0), allow_none=True)
    announce_hold_time_on_entry = StrictBoolean()
    ignore_forward = StrictBoolean(attribute='ignore_forward_bool')
    preprocess_subroutine = fields.String(validate=Length(max=39), allow_none=True)
    music_on_hold = fields.String(validate=Length(max=128), allow_none=True)
    wait_time_threshold = fields.Integer(validate=Range(min=0), allow_none=True)
    wait_time_destination = DestinationField(allow_none=True)
    wait_ratio_threshold = fields.Float(validate=Range(min=0), allow_none=True)
    wait_ratio_destination = DestinationField(allow_none=True)
    caller_id_mode = fields.String(validate=OneOf(['prepend', 'overwrite', 'append']), allow_none=True)
    caller_id_name = fields.String(validate=Length(max=80), allow_none=True)
    enabled = StrictBoolean()
    options = fields.List(fields.List(fields.String(), validate=Length(equal=2)))
    links = ListLink(Link('queues'))

    @post_load
    def create_objects(self, data):
        for key in ('wait_time_destination', 'wait_ratio_destination'):
            if data.get(key):
                data[key] = Dialaction(**data[key])
