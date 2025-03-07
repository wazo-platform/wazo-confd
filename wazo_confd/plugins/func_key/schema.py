# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for
from marshmallow import EXCLUDE, Schema, fields, validates, post_dump, pre_load
from marshmallow.validate import OneOf, Regexp, Range, Length
from marshmallow.exceptions import ValidationError

from wazo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink, Nested

EXTEN_REGEX = r'^[A-Z0-9+*]+$'


class BaseDestinationSchema(Schema):
    type = fields.String(
        validate=OneOf(
            [
                'agent',
                'bsfilter',
                'conference',
                'custom',
                'forward',
                'group',
                'groupmember',
                'onlinerec',
                'paging',
                'park_position',
                'parking',
                'queue',
                'service',
                'transfer',
                'user',
            ]
        ),
        required=True,
    )

    href = fields.String(dump_default=None, allow_none=True, dump_only=True)

    @validates('type')
    def exclude_destination(self, data):
        if data in self.context.get('exclude_destination', []):
            raise ValidationError(
                'The "{}" funckey are excluded'.format(data),
                field_name='type',
            )

    def get_parameters(self):
        parameters = []
        exclude_fields = ['href', 'type']
        for field_name, field_obj in self.declared_fields.items():
            if (
                field_name is None
                or field_name in exclude_fields
                or field_obj.dump_only
            ):
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

    user = Nested(
        'UserSchema',
        attribute='userfeatures',
        only=['firstname', 'lastname'],
        dump_only=True,
    )

    endpoint_list = 'users_list'

    @post_dump
    def generate_href(self, output, **kwargs):
        user_id = output['user_id']
        output['href'] = url_for('users', id=user_id, _external=True)
        return output

    @post_dump
    def make_user_fields_flat(self, data, **kwargs):
        if data.get('user'):
            data['user_firstname'] = data['user']['firstname']
            data['user_lastname'] = data['user']['lastname']

        data.pop('user', None)
        return data


class GroupDestinationSchema(BaseDestinationSchema):
    group_id = fields.Integer(required=True)

    group = Nested(
        'GroupSchema', attribute='groupfeatures', only=['label', 'name'], dump_only=True
    )

    @post_dump
    def make_group_fields_flat(self, data, **kwargs):
        if data.get('group'):
            # TODO(pc-m): Label was added in 21.04 group_name should be remove when we remove
            #             the compatibility logic in group schema
            data['group_name'] = data['group']['name']
            data['group_label'] = data['group']['label']

        data.pop('group', None)
        return data


class GroupMemberDestinationSchema(BaseDestinationSchema):
    group_id = fields.Integer(required=True)
    action = fields.String(validate=OneOf(['join', 'leave', 'toggle']), required=True)

    group = Nested(
        'GroupSchema', attribute='groupfeatures', only=['label', 'name'], dump_only=True
    )

    @post_dump
    def make_group_fields_flat(self, data, **kwargs):
        if data.get('group'):
            # TODO(pc-m): Label was added in 21.04 group_name should be remove when we remove
            #             the compatibility logic in group schema
            data['group_name'] = data['group']['name']
            data['group_label'] = data['group']['label']

        data.pop('group', None)
        return data

class QueueDestinationSchema(BaseDestinationSchema):
    queue_id = fields.Integer(required=True)

    queue = Nested(
        'QueueSchema', attribute='queuefeatures', only=['name'], dump_only=True
    )

    @post_dump
    def make_queue_fields_flat(self, data, **kwargs):
        if data.get('queue'):
            data['queue_name'] = data['queue']['name']

        data.pop('queue', None)
        return data


class ConferenceDestinationSchema(BaseDestinationSchema):
    conference_id = fields.Integer(required=True)

    conference = Nested(
        'ConferenceSchema', attribute='conferencefeatures', only=['name'], dump_only=True
    )

    @post_dump
    def make_conference_fields_flat(self, data, **kwargs):
        if data.get('conference'):
            data['conference_name'] = data['conference']['name']

        data.pop('conference', None)
        return data


class PagingDestinationSchema(BaseDestinationSchema):
    paging_id = fields.Integer(required=True)

    paging = Nested(
        'PagingSchema', attribute='pagingfeatures', only=['name'], dump_only=True
    )

    @post_dump
    def make_paging_fields_flat(self, data, **kwargs):
        if data.get('paging'):
            data['paging_name'] = data['paging']['name']

        data.pop('paging', None)
        return data


class ServiceDestinationSchema(BaseDestinationSchema):
    service = fields.String(
        validate=OneOf(
            [
                "enablevm",
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
                "enablednd",
            ]
        ),
        required=True,
    )


class CustomDestinationSchema(BaseDestinationSchema):
    exten = fields.String(validate=Regexp(EXTEN_REGEX), required=True)

    @pre_load
    def remove_invalid_white_spaces(self, data, **kwargs):
        exten = data.get('exten')
        if exten and isinstance(exten, str):
            data['exten'] = exten.strip()
        return data


class ForwardDestinationSchema(BaseDestinationSchema):
    forward = fields.String(
        validate=OneOf(['busy', 'noanswer', 'unconditional']), required=True
    )
    exten = fields.String(validate=Regexp(EXTEN_REGEX), allow_none=True)

    @pre_load
    def remove_invalid_white_spaces(self, data, **kwargs):
        exten = data.get('exten')
        if exten and isinstance(exten, str):
            data['exten'] = exten.strip()
        return data


class TransferDestinationSchema(BaseDestinationSchema):
    transfer = fields.String(validate=OneOf(['blind', 'attended']), required=True)


class ParkPositionDestinationSchema(BaseDestinationSchema):
    parking_lot_id = fields.Integer(required=True)
    position = fields.Integer(required=True)

    parking_lot = Nested('ParkingLotSchema', only=['name'], dump_only=True)

    @post_dump
    def make_parking_lot_fields_flat(self, data, **kwargs):
        if data.get('parking_lot'):
            data['parking_lot_name'] = data['parking_lot']['name']

        data.pop('parking_lot', None)
        return data


class ParkingDestinationSchema(BaseDestinationSchema):
    parking_lot_id = fields.Integer(required=True)

    parking_lot = Nested('ParkingLotSchema', only=['name'], dump_only=True)

    @post_dump
    def make_parking_lot_fields_flat(self, data, **kwargs):
        if data.get('parking_lot'):
            data['parking_lot_name'] = data['parking_lot']['name']

        data.pop('parking_lot', None)
        return data


class BSFilterDestinationSchema(BaseDestinationSchema):
    filter_member_id = fields.Integer(required=True)

    filter_member = Nested(
        '_BSFilterMemberDestinationSchema',
        attribute='filtermember',
        dump_only=True,
        load_default={},
    )

    @post_dump
    def make_member_fields_flat(self, data, **kwargs):
        if data['filter_member'].get('user'):
            data['filter_member_firstname'] = data['filter_member']['user']['firstname']
            data['filter_member_lastname'] = data['filter_member']['user']['lastname']

        data.pop('filter_member', None)
        return data


class _BSFilterMemberDestinationSchema(Schema):
    user = Nested('UserSchema', only=['firstname', 'lastname'], dump_only=True)


class AgentDestinationSchema(BaseDestinationSchema):
    agent_id = fields.Integer(required=True)
    action = fields.String(validate=OneOf(['login', 'logout', 'toggle']), required=True)


class OnlineRecordingDestinationSchema(BaseDestinationSchema):
    pass


class FuncKeyDestinationField(Nested):
    destination_schemas = {
        'agent': AgentDestinationSchema,
        'bsfilter': BSFilterDestinationSchema,
        'conference': ConferenceDestinationSchema,
        'custom': CustomDestinationSchema,
        'forward': ForwardDestinationSchema,
        'group': GroupDestinationSchema,
        'groupmember': GroupMemberDestinationSchema,
        'onlinerec': OnlineRecordingDestinationSchema,
        'paging': PagingDestinationSchema,
        'park_position': ParkPositionDestinationSchema,
        'parking': ParkingDestinationSchema,
        'queue': QueueDestinationSchema,
        'service': ServiceDestinationSchema,
        'transfer': TransferDestinationSchema,
        'user': UserDestinationSchema,
    }

    def __init__(self, *args, **kwargs):
        kwargs['unknown'] = EXCLUDE
        super().__init__(*args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        self.schema.context = self.context
        base = super()._deserialize(value, attr, data, **kwargs)
        return Nested(
            self.destination_schemas[base['type']], unknown=self.unknown
        )._deserialize(value, attr, data, **kwargs)

    def _serialize(self, nested_obj, attr, obj):
        base = super()._serialize(nested_obj, attr, obj)
        return Nested(
            self.destination_schemas[base['type']], unknown=self.unknown
        )._serialize(nested_obj, attr, obj)


class FuncKeySchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    inherited = fields.Boolean(dump_only=True)
    blf = StrictBoolean()
    label = fields.String(allow_none=True)
    destination = FuncKeyDestinationField(BaseDestinationSchema, required=True)


class FuncKeyPositionField(fields.Field):
    def __init__(self, key_field, nested_field, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_field = key_field
        self.nested_field = nested_field
        self.nested_field.schema.handle_error = lambda *args, **kwargs: None

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, dict):
            raise ValidationError('FuncKey must be a dictionary')

        template = {}
        for raw_position, raw_funckey in value.items():
            position = self.key_field.deserialize(raw_position, attr, data, **kwargs)
            self.nested_field.schema.context = self.context
            try:
                funckey = self.nested_field.deserialize(
                    raw_funckey, attr, data, **kwargs
                )
            except ValidationError as e:
                nested_errors = {str(position): e.messages}
                raise ValidationError(nested_errors, data=data)
            template[position] = funckey
        return template

    def _serialize(self, value, attr, obj):
        template = {}
        for raw_position, raw_funckey in value.items():
            position = self.key_field._serialize(raw_position, attr, obj)
            funckey = self.nested_field.serialize(raw_position, getattr(obj, attr))
            template[position] = funckey
        return template


class FuncKeyTemplateSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(validate=Length(max=128))
    keys = FuncKeyPositionField(
        fields.Integer(validate=Range(min=1)),
        Nested(FuncKeySchema, required=True),
    )
    links = ListLink(Link('func_keys_templates'))


class FuncKeyUnifiedTemplateSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=128))
    keys = FuncKeyPositionField(
        fields.Integer(validate=Range(min=1)),
        Nested(FuncKeySchema, required=True),
    )


class FuncKeyTemplateUserSchema(BaseSchema):
    user_id = fields.Integer(attribute='id')
    template_id = fields.Integer(attribute='func_key_template_id')
    links = ListLink(
        Link('func_keys_templates', field='func_key_template_id', target='id'),
        Link('users', field='id'),
    )
