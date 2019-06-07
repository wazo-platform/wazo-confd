# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load
from marshmallow.validate import Length, Range, Regexp

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.ivr_choice import IVRChoice

from wazo_confd.helpers.destination import DestinationField
from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink
from wazo_confd.helpers.validator import EXTEN_REGEX


class IvrChoiceSchema(BaseSchema):
    exten = fields.String(validate=Regexp(EXTEN_REGEX), required=True)
    destination = DestinationField(required=True)


class IvrSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(validate=Length(max=128), required=True)
    description = fields.String(allow_none=True)
    greeting_sound = fields.String(validate=Length(max=255), allow_none=True)
    menu_sound = fields.String(validate=Length(max=255), required=True)
    invalid_sound = fields.String(validate=Length(max=255), allow_none=True)
    abort_sound = fields.String(validate=Length(max=255), allow_none=True)
    timeout = fields.Integer(validate=Range(min=0))
    max_tries = fields.Integer(validate=Range(min=1))
    invalid_destination = DestinationField(allow_none=True)
    timeout_destination = DestinationField(allow_none=True)
    abort_destination = DestinationField(allow_none=True)
    choices = fields.Nested(IvrChoiceSchema, many=True)
    links = ListLink(Link('ivr'))

    incalls = fields.Nested(
        'IncallSchema',
        only=[
            'id',
            'extensions',
            'links'
        ],
        many=True,
        dump_only=True,
    )

    @post_load
    def create_objects(self, data):
        for key in ['invalid_destination', 'timeout_destination', 'abort_destination']:
            if data.get(key):
                data[key] = Dialaction(**data[key])
        if 'choices' in data:
            data['choices'] = [
                IVRChoice(exten=choice['exten'], destination=Dialaction(**choice['destination']))
                for choice in data['choices']
            ]
