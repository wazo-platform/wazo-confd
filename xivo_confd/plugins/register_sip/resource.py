# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from flask import url_for, request
from marshmallow import fields, post_load, pre_dump, validates_schema
from marshmallow.exceptions import ValidationError
from marshmallow.validate import OneOf, Range, Regexp

from xivo_dao.alchemy.staticsip import StaticSIP

from xivo_confd.auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean
from xivo_confd.helpers.restful import ListResource, ItemResource

REGISTER_REGEX = re.compile(r'''^
                            (?:(?P<transport>.*)://)?
                            (?P<sip_username>[^:/]*)
                            (?::(?P<auth_password>[^:/]*))?
                            (?::(?P<auth_username>[^:/]*))?
                            @
                            (?P<remote_host>[^:~/]*)
                            (?::(?P<remote_port>\d*))?
                            (?:/(?P<callback_extension>[^~]*))?
                            (?:~(?P<expiration>\d*))?
                            $''', re.VERBOSE)

INVALID_CHAR = r'^[^:/ ]*$'
INVALID_REMOTE_HOST = r'^[^:/~ ]*$'
INVALID_CALLBACK_EXTENSION = r'^[^~ ]*$'


class RegisterSIPSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    transport = fields.String(validate=OneOf(['udp', 'tcp', 'tls', 'ws', 'wss']), allow_none=True)
    sip_username = fields.String(validate=Regexp(INVALID_CHAR), required=True)
    auth_username = fields.String(validate=Regexp(INVALID_CHAR), allow_none=True)
    auth_password = fields.String(validate=Regexp(INVALID_CHAR), allow_none=True)
    remote_host = fields.String(validate=Regexp(INVALID_REMOTE_HOST), required=True)
    remote_port = fields.Integer(validate=Range(min=0, max=65535), allow_none=True)
    callback_extension = fields.String(validate=Regexp(INVALID_CALLBACK_EXTENSION), allow_none=True)
    expiration = fields.Integer(validate=Range(min=0), allow_none=True)
    enabled = StrictBoolean(missing=True)
    links = ListLink(Link('register_sip'))

    trunk = fields.Nested('TrunkSchema', only=['id', 'links'], dump_only=True)

    @validates_schema
    def validate_auth_username(self, data):
        if data.get('auth_username') and not data.get('auth_password'):
            raise ValidationError('Cannot set field "auth_username" if the field "auth_password" is not set',
                                  'auth_username')

    @validates_schema
    def validate_total_length(self, data):
        if len(self.convert_to_chansip(data)['var_val']) > 255:
            raise ValidationError('The sum of all fields is longer than maximum length 255')

    @post_load
    def convert_to_chansip(self, data):
        chansip_fmt = '{transport}{sip_username}{auth_password}{auth_username}'\
                      '@{remote_host}{remote_port}{callback_extension}{expiration}'
        data['var_val'] = chansip_fmt.format(
            transport='{}://'.format(data.get('transport')) if data.get('transport') else '',
            sip_username=data.get('sip_username'),
            auth_password=':{}'.format(data.get('auth_password')) if data.get('auth_password') else '',
            auth_username=':{}'.format(data.get('auth_username')) if data.get('auth_username') else '',
            remote_host=data.get('remote_host'),
            remote_port=':{}'.format(data.get('remote_port')) if data.get('remote_port') else '',
            callback_extension='/{}'.format(data.get('callback_extension')) if data.get('callback_extension') else '',
            expiration='~{}'.format(data.get('expiration')) if data.get('expiration') else '',
        )
        return data

    @pre_dump
    def convert_from_chansip(self, data):
        register = REGISTER_REGEX.match(data.var_val)
        result = register.groupdict()
        result['id'] = data.id
        result['enabled'] = data.enabled
        result['trunk'] = data.trunk
        return result


class RegisterSIPList(ListResource):

    model = StaticSIP
    schema = RegisterSIPSchema

    def build_headers(self, register):
        return {'Location': url_for('register_sip', id=register.id, _external=True)}

    @required_acl('confd.registers.create')
    def post(self):
        form = self.schema().load(request.get_json()).data
        model = self.model(filename='sip.conf',
                           category='general',
                           var_name='register',
                           var_val=form['var_val'],
                           enabled=form['enabled'])
        model = self.service.create(model)
        return self.schema().dump(model).data, 201, self.build_headers(model)

    @required_acl('confd.registers.read')
    def get(self):
        return super(RegisterSIPList, self).get()


class RegisterSIPItem(ItemResource):

    schema = RegisterSIPSchema

    @required_acl('confd.registers.{id}.read')
    def get(self, id):
        return super(RegisterSIPItem, self).get(id)

    @required_acl('confd.registers.{id}.update')
    def put(self, id):
        model = self.service.get(id)
        form = self.schema().load(request.get_json(), partial=True).data

        model_json = self.schema().dump(model).data
        for name, value in form.items():
            model_json[name] = value
        model_json = self.schema().load(model_json).data  # update var_val

        model.var_val = model_json['var_val']
        model.enabled = model_json['enabled']
        self.service.edit(model)
        return '', 204

    @required_acl('confd.registers.{id}.delete')
    def delete(self, id):
        return super(RegisterSIPItem, self).delete(id)
