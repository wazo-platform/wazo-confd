# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields, post_load, pre_dump
from marshmallow.validate import Length, OneOf

from xivo_dao.alchemy.application_dest_node import ApplicationDestNode

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink


class NodeApplicationDestinationOptionsSchema(BaseSchema):

    type = fields.String(
        attribute='type_',
        validate=OneOf(['mixing', 'holding']),
        required=True,
        missing='holding',
    )
    music_on_hold = fields.String(validate=Length(max=128), allow_none=True, missing=None)


class ApplicationDestinationOptionsField(fields.Field):

    _options = {
        'node': fields.Nested(NodeApplicationDestinationOptionsSchema),
    }

    def _deserialize(self, value, attr, data):
        destination = data.get('destination')
        concrete_options = self._options.get(destination)
        if not concrete_options:
            return {}
        return concrete_options._deserialize(value, attr, data)

    def _serialize(self, value, attr, obj):
        destination = obj.destination
        concrete_options = self._options.get(destination)
        if not concrete_options:
            return {}
        return concrete_options._serialize(value, attr, obj)


class ApplicationSchema(BaseSchema):
    uuid = fields.String(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(validate=Length(max=128), allow_none=True)
    destination = fields.String(
        validate=OneOf(ApplicationDestinationOptionsField._options.keys()),
        allow_none=True,
        default=None,
    )
    destination_options = ApplicationDestinationOptionsField(default={})
    links = ListLink(Link('applications', field='uuid', target='application_uuid'))

    @pre_dump
    def map_destination(self, obj):
        if obj.dest_node:
            obj.destination = 'node'
            obj.destination_options = obj.dest_node

    @post_load
    def create_objects(self, data):
        dest = data.pop('destination', None)
        dest_options = data.pop('destination_options', {})
        if dest == 'node':
            data['dest_node'] = ApplicationDestNode(**dest_options)
