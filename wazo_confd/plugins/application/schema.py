# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load, pre_dump
from marshmallow.validate import Length, OneOf
from xivo_dao.alchemy.application_dest_node import ApplicationDestNode

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, Nested


class NodeApplicationDestinationOptionsSchema(BaseSchema):
    type = fields.String(attribute='type_', validate=OneOf(['holding']), required=True)
    music_on_hold = fields.String(
        validate=Length(max=128), allow_none=True, load_default=None
    )
    answer = fields.Boolean(load_default=False)


class ApplicationDestinationOptionsField(fields.Field):
    _options = {'node': Nested(NodeApplicationDestinationOptionsSchema)}

    def _deserialize(self, value, attr, data, **kwargs):
        destination = data.get('destination')
        concrete_options = self._options.get(destination)
        if not concrete_options:
            return {}
        return concrete_options._deserialize(value, attr, data, **kwargs)

    def _serialize(self, value, attr, obj):
        if not obj.dest_node:
            return {}
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
        dump_default=None,
    )
    destination_options = ApplicationDestinationOptionsField(dump_default={})
    links = ListLink(Link('applications', field='uuid', target='application_uuid'))

    lines = Nested(
        'LineSchema', only=['id', 'name', 'links'], many=True, dump_only=True
    )

    @pre_dump
    def map_destination(self, obj, **kwargs):
        if obj.dest_node:
            obj.destination = 'node'
            obj.destination_options = obj.dest_node
        return obj

    @post_load
    def create_objects(self, data, **kwargs):
        dest = data.pop('destination', None)
        dest_options = data.pop('destination_options', {})
        data['dest_node'] = None
        if dest == 'node':
            data['dest_node'] = ApplicationDestNode(**dest_options)
        return data
