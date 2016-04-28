# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from flask import request
from flask_restful import Resource
from marshmallow import fields, validates_schema, validates
from marshmallow.validate import Equal, Regexp, Length, OneOf, Predicate, Range
from marshmallow.exceptions import ValidationError

from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean
from .access_restriction import xivo_unconfigured

ADMIN_PASSWORD_REGEX = r'^[a-zA-Z0-9\/\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\-]{4,64}$'
IP_ADDRESS_REGEX = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
BASE_HOSTNAME_REGEX = r'[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'
HOSTNAME_REGEX = r'^{}$'.format(BASE_HOSTNAME_REGEX)
DOMAIN_REGEX = r'^(?:{}\.)*({})$'.format(BASE_HOSTNAME_REGEX, BASE_HOSTNAME_REGEX)
INTERFACE_REGEX = r'^[\w\-\:\.]{1,64}$'


class WizardNetworkSchema(BaseSchema):
    hostname = fields.String(validate=(Regexp(HOSTNAME_REGEX), Length(max=63)), required=True)
    ip_address = fields.String(validate=Regexp(IP_ADDRESS_REGEX), required=True)
    domain = fields.String(validate=(Regexp(DOMAIN_REGEX), Length(max=255)), required=True)
    interface = fields.String(validate=Regexp(INTERFACE_REGEX), required=True)
    netmask = fields.String(validate=Regexp(IP_ADDRESS_REGEX), required=True)
    gateway = fields.String(validate=Regexp(IP_ADDRESS_REGEX), required=True)
    nameservers = fields.List(fields.String(validate=Regexp(IP_ADDRESS_REGEX)), validate=Length(max=3), required=True)


class WizardContextOutcallSchema(BaseSchema):
    display_name = fields.String(validate=Length(min=3, max=128), missing='Outcalls')


class WizardContextInternalSchema(BaseSchema):
    display_name = fields.String(validate=Length(min=3, max=128), missing='Default')
    number_start = fields.String(validate=(Predicate('isdigit'), Length(max=16)), required=True)
    number_end = fields.String(validate=(Predicate('isdigit'), Length(max=16)), required=True)

    @validates_schema
    def validate_numbers(self, data):
        if not data.get('number_start') and not data.get('number_end'):
            return
        if not data.get('number_start') or not data.get('number_end'):
            raise ValidationError('Both numbers, number_start and number_end, must be set')

        if len(data['number_start']) != len(data['number_end']):
            raise ValidationError('Numbers do not have de same length')

        if int(data['number_start']) > int(data['number_end']):
            raise ValidationError('It is not a valid interval')


class WizardContextIncallSchema(WizardContextInternalSchema):
    display_name = fields.String(validate=Length(min=3, max=128), missing='Incalls')
    did_length = fields.Integer(validate=Range(min=0, max=20))
    number_start = fields.String(validate=(Predicate('isdigit'), Length(max=16)))
    number_end = fields.String(validate=(Predicate('isdigit'), Length(max=16)))

    @validates_schema
    def validate_numbers(self, data):
        super(WizardContextIncallSchema, self).validate_numbers(data)
        if data.get('number_start') and data.get('number_end'):
            if not data.get('did_length'):
                raise ValidationError('Missing data for required field.', 'did_length')


class WizardSchema(BaseSchema):
    xivo_uuid = fields.UUID(dump_only=True)
    admin_username = fields.Constant(constant='root', dump_only=True)
    admin_password = fields.String(validate=Regexp(ADMIN_PASSWORD_REGEX), required=True)
    license = StrictBoolean(validate=Equal(True), required=True)
    language = fields.String(validate=OneOf(['en_US', 'fr_FR']), missing='en_US')
    entity_name = fields.String(validate=Length(min=3, max=64), required=True)
    timezone = fields.String(validate=Length(max=128), required=True)
    network = fields.Nested(WizardNetworkSchema, required=True)
    context_internal = fields.Nested(WizardContextInternalSchema, required=True)
    context_outcall = fields.Nested(WizardContextOutcallSchema, missing=WizardContextOutcallSchema().load({}).data)
    context_incall = fields.Nested(WizardContextIncallSchema, missing=WizardContextIncallSchema().load({}).data)

    @validates('entity_name')
    def validate_entity_name(self, entity_name):
        sub_name = ''.join(c for c in entity_name if c.isalnum())
        if len(sub_name) < 3:
            raise ValidationError('Shorter than alphanumeric minimum length 3.')


class ConfiguredSchema(BaseSchema):
    configured = fields.Boolean()


class WizardResource(Resource):

    wizard_schema = WizardSchema()
    configured_schema = ConfiguredSchema()

    def __init__(self, service):
        self.service = service

    def get(self):
        configured = self.service.get()
        return self.configured_schema.dump(configured).data

    @xivo_unconfigured
    def post(self):
        wizard = self.wizard_schema.load(request.get_json()).data
        wizard_with_uuid = self.service.create(wizard)
        return self.wizard_schema.dump(wizard_with_uuid).data


class WizardDiscoverInterfaceSchema(BaseSchema):
    ip_address = fields.String()
    interface = fields.String()
    netmask = fields.String()


class WizardDiscoverGatewaySchema(BaseSchema):
    gateway = fields.String()
    interface = fields.String()


class WizardDiscoverSchema(BaseSchema):
    hostname = fields.String()
    nameservers = fields.List(fields.String())
    domain = fields.String()
    timezone = fields.String()
    interfaces = fields.List(fields.Nested(WizardDiscoverInterfaceSchema))
    gateways = fields.List(fields.Nested(WizardDiscoverGatewaySchema))


class WizardDiscoverResource(Resource):

    schema = WizardDiscoverSchema()

    def __init__(self, service):
        self.service = service

    @xivo_unconfigured
    def get(self):

        discover = {'interfaces': self.service.get_interfaces(),
                    'gateways': self.service.get_gateways(),
                    'nameservers': self.service.get_nameservers(),
                    'hostname': self.service.get_hostname(),
                    'timezone': self.service.get_timezone(),
                    'domain': self.service.get_domain()}
        return self.schema.dump(discover).data
