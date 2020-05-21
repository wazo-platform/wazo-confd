# Copyright 2017-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from flask import url_for, request
from marshmallow import fields, post_load, pre_dump, validates_schema
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Range, Regexp

from xivo_dao.alchemy.staticiax import StaticIAX

from wazo_confd.auth import required_acl
from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean
from wazo_confd.helpers.restful import ListResource, ItemResource

REGISTER_REGEX = re.compile(
    r'''^
    (?:
    (?P<auth_username>[^:/]*)
    (?::(?P<auth_password>[^:/]*))?
    @)?
    (?P<remote_host>[^:?/]*)
    (?::(?P<remote_port>\d*))?
    (?:/(?P<callback_extension>[^?]*))?
    (?:\?(?P<callback_context>.*))?
    $''',
    re.VERBOSE,
)

INVALID_CHAR = r'^[^:/ ]*$'
INVALID_REMOTE_HOST = r'^[^:/? ]*$'
INVALID_CALLBACK_EXTENSION = r'^[^? ]*$'


class RegisterIAXSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    auth_username = fields.String(validate=Regexp(INVALID_CHAR), allow_none=True)
    auth_password = fields.String(validate=Regexp(INVALID_CHAR), allow_none=True)
    remote_host = fields.String(validate=Regexp(INVALID_REMOTE_HOST), required=True)
    remote_port = fields.Integer(validate=Range(min=0, max=65535), allow_none=True)
    callback_extension = fields.String(
        validate=Regexp(INVALID_CALLBACK_EXTENSION), allow_none=True
    )
    callback_context = fields.String(allow_none=True)
    enabled = StrictBoolean(missing=True)
    links = ListLink(Link('register_iax'))

    trunk = fields.Nested('TrunkSchema', only=['id', 'links'], dump_only=True)

    @validates_schema
    def validate_auth_username(self, data):
        if data.get('auth_username') and not data.get('auth_password'):
            raise ValidationError(
                'Cannot set field "auth_username" if the field "auth_password" is not set',
                'auth_username',
            )

    @validates_schema
    def validate_callback_context(self, data):
        if data.get('callback_context') and not data.get('callback_extension'):
            raise ValidationError(
                'Cannot set field "callback_context" if the field "callback_extension" is not set',
                'callback_context',
            )

    @validates_schema
    def validate_total_length(self, data):
        if len(self.convert_to_chaniax(data)['var_val']) > 255:
            raise ValidationError(
                'The sum of all fields is longer than maximum length 255'
            )

    @post_load
    def convert_to_chaniax(self, data):
        chaniax_fmt = (
            '{auth_username}{auth_password}{separator}'
            '{remote_host}{remote_port}{callback_extension}{callback_context}'
        )
        data['var_val'] = chaniax_fmt.format(
            auth_username=data.get('auth_username')
            if data.get('auth_username')
            else '',
            auth_password=':{}'.format(data.get('auth_password'))
            if data.get('auth_password')
            else '',
            separator='@'
            if data.get('auth_username') or data.get('auth_password')
            else '',
            remote_host=data.get('remote_host'),
            remote_port=':{}'.format(data.get('remote_port'))
            if data.get('remote_port')
            else '',
            callback_extension='/{}'.format(data.get('callback_extension'))
            if data.get('callback_extension')
            else '',
            callback_context='?{}'.format(data.get('callback_context'))
            if data.get('callback_context')
            else '',
        )
        return data

    @pre_dump
    def convert_from_chaniax(self, data):
        register = REGISTER_REGEX.match(data.var_val)
        result = register.groupdict()
        result['id'] = data.id
        result['enabled'] = data.enabled
        result['trunk'] = data.trunk
        return result


class RegisterIAXList(ListResource):

    model = StaticIAX
    schema = RegisterIAXSchema

    def build_headers(self, register):
        return {'Location': url_for('register_iax', id=register.id, _external=True)}

    @required_acl('confd.registers.create')
    def post(self):
        form = self.schema().load(request.get_json())
        model = self.model(
            filename='iax.conf',
            category='general',
            var_name='register',
            var_val=form['var_val'],
            enabled=form['enabled'],
        )
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)

    @required_acl('confd.registers.read')
    def get(self):
        return super().get()


class RegisterIAXItem(ItemResource):

    schema = RegisterIAXSchema

    @required_acl('confd.registers.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.registers.{id}.update')
    def put(self, id):
        model = self.service.get(id)
        form = self.schema().load(request.get_json(), partial=True)

        model_json = self.schema().dump(model)
        for name, value in form.items():
            model_json[name] = value
        model_json = self.schema().load(model_json)  # update var_val

        model.var_val = model_json['var_val']
        model.enabled = model_json['enabled']
        self.service.edit(model)
        return '', 204

    @required_acl('confd.registers.{id}.delete')
    def delete(self, id):
        return super().delete(id)
