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
from marshmallow import fields
from marshmallow.validate import Equal, Regexp, Length, OneOf

from xivo_dao.helpers import errors
from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean

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


class WizardSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    admin_username = fields.Constant(constant='root', dump_only=True)
    admin_password = fields.String(validate=Regexp(ADMIN_PASSWORD_REGEX), required=True)
    license = StrictBoolean(validate=Equal(True), required=True)
    language = fields.String(validate=OneOf(['en_US', 'fr_FR']), default='en_US')
    entity_name = fields.String(validate=Length(min=3, max=64), default='xivo')
    timezone = fields.String(validate=Length(max=128), required=True)
    network = fields.Nested(WizardNetworkSchema)


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

    def post(self):
        if self.service.get().configured:
            raise errors.xivo_already_configured()

        wizard = self.wizard_schema.load(request.get_json()).data
        wizard_with_uuid = self.service.created(wizard)
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

    def get(self):
        if self.service.get().configured:
            raise errors.xivo_already_configured()

        discover = {'interfaces': self.service.get_interfaces(),
                    'gateways': self.service.get_gateways(),
                    'nameservers': self.service.get_nameservers(),
                    'hostname': self.service.get_hostname(),
                    'timezone': self.service.get_timezone(),
                    'domain': self.service.get_domain()}
        return self.schema.dump(discover).data
