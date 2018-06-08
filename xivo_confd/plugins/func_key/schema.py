# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import re

from flask import url_for
from marshmallow import Schema, fields, validates, post_dump
from marshmallow.validate import OneOf, Regexp, Range, Length
from marshmallow.exceptions import ValidationError

from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink

EXTEN_REGEX = re.compile(r'[A-Z0-9+*]+')


class BaseDestinationSchema(Schema):
    type = fields.String(validate=OneOf(['user',
                                         'group',
                                         'queue',
                                         'conference',
                                         'paging',
                                         'service',
                                         'custom',
                                         'forward',
                                         'transfer',
                                         'park_position',
                                         'parking',
                                         'bsfilter',
                                         'agent',
                                         'onlinerec']),
                         required=True)

    href = fields.String(default=None, allow_none=True, dump_only=True)

    @validates('type')
    def exclude_destination(self, data):
        if data in self.context.get('exclude_destination', []):
            raise ValidationError('The "{}" funckey are excluded'.format(data), 'type')

    def get_parameters(self):
        parameters = []
        exclude_fields = ['href', 'type']
        for field_name, field_obj in self.declared_fields.iteritems():
            if field_name is None or field_name in exclude_fields or field_obj.dump_only:
                continue

            parameter = {'name': field_name}
            if isinstance(field_obj.validate, OneOf):
                parameter['values'] = field_obj.validate.choices
            if getattr(self, 'endpoint_list', False):
                parameter['collection'] = url_for(self.endpoint_list, _external=True)
            parameters.append(parameter)
        return parameters


class UserDestinationSchema(BaseDestinationSchema):
    user_id = fields.Integer(required=True)

    user = fields.Nested('UserSchema',
                         attribute='userfeatures',
                         only=['firstname',
                               'lastname'],
                         dump_only=True)

    endpoint_list = 'users_list'

    @post_dump
    def generate_href(self, output):
        user_id = output['user_id']
        output['href'] = url_for('users', id=user_id, _external=True)
        return output

    @post_dump
    def make_user_fields_flat(self, data):
        if data.get('user'):
            data['user_firstname'] = data['user']['firstname']
            data['user_lastname'] = data['user']['lastname']

        data.pop('user', None)
        return data


class GroupDestinationSchema(BaseDestinationSchema):
    group_id = fields.Integer(required=True)

    group = fields.Nested('GroupSchema',
                          attribute='groupfeatures',
                          only=['name'],
                          dump_only=True)

    @post_dump
    def make_group_fields_flat(self, data):
        if data.get('group'):
            data['group_name'] = data['group']['name']

        data.pop('group', None)
        return data


class QueueDestinationSchema(BaseDestinationSchema):
    queue_id = fields.Integer(required=True)


class ConferenceDestinationSchema(BaseDestinationSchema):
    conference_id = fields.Integer(required=True)


class PagingDestinationSchema(BaseDestinationSchema):
    paging_id = fields.Integer(required=True)


class ServiceDestinationSchema(BaseDestinationSchema):
    service = fields.String(validate=OneOf(["enablevm",
                                            "vmusermsg",
                                            "vmuserpurge",
                                            "phonestatus",
                                            "recsnd",
                                            "calllistening",
                                            "directoryaccess",
                                            "fwdundoall",
                                            "pickup",
                                            "callrecord",
                                            "incallfilter",
                                            "enablednd"]),
                            required=True)


class CustomDestinationSchema(BaseDestinationSchema):
    exten = fields.String(validate=Regexp(EXTEN_REGEX), required=True)


class ForwardDestinationSchema(BaseDestinationSchema):
    forward = fields.String(validate=OneOf(['busy', 'noanswer', 'unconditional']),
                            required=True)
    exten = fields.String(validate=Regexp(EXTEN_REGEX), allow_none=True)


class TransferDestinationSchema(BaseDestinationSchema):
    transfer = fields.String(validate=OneOf(['blind', 'attended']),
                             required=True)


class ParkPositionDestinationSchema(BaseDestinationSchema):
    position = fields.Integer(required=True)


class ParkingDestinationSchema(BaseDestinationSchema):
    pass


class BSFilterDestinationSchema(BaseDestinationSchema):
    filter_member_id = fields.Integer(required=True)


class AgentDestinationSchema(BaseDestinationSchema):
    agent_id = fields.Integer(required=True)
    action = fields.String(validate=OneOf(['login', 'logout', 'toggle']),
                           required=True)


class OnlineRecordingDestinationSchema(BaseDestinationSchema):
    pass


class FuncKeyDestinationField(fields.Nested):

    destination_schemas = {'user': UserDestinationSchema,
                           'group': GroupDestinationSchema,
                           'queue': QueueDestinationSchema,
                           'conference': ConferenceDestinationSchema,
                           'paging': PagingDestinationSchema,
                           'service': ServiceDestinationSchema,
                           'custom': CustomDestinationSchema,
                           'forward': ForwardDestinationSchema,
                           'transfer': TransferDestinationSchema,
                           'park_position': ParkPositionDestinationSchema,
                           'parking': ParkingDestinationSchema,
                           'bsfilter': BSFilterDestinationSchema,
                           'agent': AgentDestinationSchema,
                           'onlinerec': OnlineRecordingDestinationSchema}

    def _deserialize(self, value, attr, data):
        self.schema.context = self.context
        base = super(FuncKeyDestinationField, self)._deserialize(value, attr, data)
        return fields.Nested(self.destination_schemas[base['type']])._deserialize(value, attr, data)

    def _serialize(self, nested_obj, attr, obj):
        base = super(FuncKeyDestinationField, self)._serialize(nested_obj, attr, obj)
        return fields.Nested(self.destination_schemas[base['type']])._serialize(nested_obj, attr, obj)


class FuncKeySchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    inherited = fields.Boolean(dump_only=True)
    blf = StrictBoolean()
    label = fields.String(allow_none=True)
    destination = FuncKeyDestinationField(BaseDestinationSchema, required=True)


class FuncKeyPositionField(fields.Field):
    def __init__(self, key_field, nested_field, *args, **kwargs):
        super(FuncKeyPositionField, self).__init__(*args, **kwargs)
        self.key_field = key_field
        self.nested_field = nested_field
        self.nested_field.schema.handle_error = lambda _, __: None

    def _deserialize(self, value, attr, data):
        if not isinstance(value, dict):
            raise ValidationError('FuncKey must be a dictionary')

        template = {}
        for raw_position, raw_funckey in value.iteritems():
            position = self.key_field.deserialize(raw_position, attr, data)
            self.nested_field.schema.context = self.context
            try:
                funckey = self.nested_field.deserialize(raw_funckey, attr, data)
            except ValidationError as e:
                nested_errors = {str(position): e.messages}
                raise ValidationError(nested_errors, data=data)
            template[position] = funckey
        return template

    def _serialize(self, value, attr, obj):
        template = {}
        for raw_position, raw_funckey in value.iteritems():
            position = self.key_field._serialize(raw_position, attr, obj)
            funckey = self.nested_field.serialize(raw_position, self.get_value(attr, obj))
            template[position] = funckey
        return template


class FuncKeyTemplateSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=128))
    keys = FuncKeyPositionField(fields.Integer(validate=Range(min=1)),
                                fields.Nested(FuncKeySchema, required=True))
    links = ListLink(Link('func_keys_templates'))


class FuncKeyUnifiedTemplateSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=128))
    keys = FuncKeyPositionField(fields.Integer(validate=Range(min=1)),
                                fields.Nested(FuncKeySchema, required=True))


class FuncKeyTemplateUserSchema(BaseSchema):
    user_id = fields.Integer(attribute='id')
    template_id = fields.Integer(attribute='func_key_template_id')
    links = ListLink(Link('func_keys_templates',
                          field='func_key_template_id',
                          target='id'),
                     Link('users',
                          field='id'))
