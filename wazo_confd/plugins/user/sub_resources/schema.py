# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load, pre_dump
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema, Nested, StrictBoolean


class ServiceDNDSchema(BaseSchema):
    enabled = StrictBoolean(attribute='dnd_enabled', required=True)

    types = ['dnd']


class ServiceIncallFilterSchema(BaseSchema):
    enabled = StrictBoolean(attribute='incallfilter_enabled', required=True)

    types = ['incallfilter']


class ServicesSchema(BaseSchema):
    dnd = Nested(ServiceDNDSchema)
    incallfilter = Nested(ServiceIncallFilterSchema)

    types = ['dnd', 'incallfilter']

    @pre_dump()
    def add_envelope(self, data, **kwargs):
        return {type_: data for type_ in self.types}

    @post_load
    def remove_envelope(self, data, **kwargs):
        result = {}
        for service in data.values():
            for key, value in service.items():
                result[key] = value
        return result


class ForwardBusySchema(BaseSchema):
    enabled = StrictBoolean(attribute='busy_enabled')
    destination = fields.String(
        attribute='busy_destination', validate=Length(max=128), allow_none=True
    )

    types = ['busy']


class ForwardNoAnswerSchema(BaseSchema):
    enabled = StrictBoolean(attribute='noanswer_enabled')
    destination = fields.String(
        attribute='noanswer_destination', validate=Length(max=128), allow_none=True
    )

    types = ['noanswer']


class ForwardUnconditionalSchema(BaseSchema):
    enabled = StrictBoolean(attribute='unconditional_enabled')
    destination = fields.String(
        attribute='unconditional_destination', validate=Length(max=128), allow_none=True
    )

    types = ['unconditional']


class ForwardsSchema(BaseSchema):
    busy = Nested(ForwardBusySchema)
    noanswer = Nested(ForwardNoAnswerSchema)
    unconditional = Nested(ForwardUnconditionalSchema)

    types = ['busy', 'noanswer', 'unconditional']

    @pre_dump
    def add_envelope(self, data, **kwargs):
        return {type_: data for type_ in self.types}

    @post_load
    def remove_envelope(self, data, **kwargs):
        result = {}
        for forward in data.values():
            for key, value in forward.items():
                result[key] = value
        return result
