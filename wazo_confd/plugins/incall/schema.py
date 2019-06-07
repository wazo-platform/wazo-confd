# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import OneOf, Length

from xivo_confd.helpers.destination import DestinationField
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink


class IncallSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    preprocess_subroutine = fields.String(validate=Length(max=39), allow_none=True)
    caller_id_mode = fields.String(validate=OneOf(['prepend', 'overwrite', 'append']), allow_none=True)
    caller_id_name = fields.String(validate=Length(max=80), allow_none=True)
    description = fields.String(allow_none=True)
    destination = DestinationField(required=True)
    links = ListLink(Link('incalls'))

    extensions = fields.Nested('ExtensionSchema',
                               only=['id', 'exten', 'context', 'links'],
                               many=True,
                               dump_only=True)
    schedules = fields.Nested('ScheduleSchema',
                              only=['id', 'name', 'links'],
                              many=True,
                              dump_only=True)
