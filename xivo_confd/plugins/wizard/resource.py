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

import netifaces
import re

from flask import request
from flask_restful import Resource
from marshmallow import fields, post_load
from marshmallow.validate import Equal, Regexp, Length, OneOf

from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean

import logging

logger = logging.getLogger(__name__)

ADMIN_PASSWORD_REGEX = r'^[a-zA-Z0-9\/\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\-]{4,64}$'
NAMESERVER_REGEX = '^nameserver (.*)'
IP_ADDRESS_REGEX = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
BASE_HOSTNAME_REGEX = r'[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'
HOSTNAME_REGEX = r'^{}$'.format(BASE_HOSTNAME_REGEX)
DOMAIN_REGEX = r'^(?:{}\.)*({})$'.format(BASE_HOSTNAME_REGEX, BASE_HOSTNAME_REGEX)
INTERFACE_REGEX = r'^[\w\-\:\.]{1,64}$'


class WizardNetworkSchema(BaseSchema):
    hostname = fields.String(required=True, validate=(Regexp(HOSTNAME_REGEX), Length(max=63)))
    ip_address = fields.String(required=True, validate=Regexp(IP_ADDRESS_REGEX))
    domain = fields.String(required=True, validate=(Regexp(DOMAIN_REGEX), Length(max=255)))
    interface = fields.String(dump_only=True, validate=Regexp(INTERFACE_REGEX))
    netmask = fields.String(dump_only=True, validate=Regexp(IP_ADDRESS_REGEX))
    gateway = fields.String(dump_only=True, validate=Regexp(IP_ADDRESS_REGEX))
    nameservers = fields.List(fields.String(validate=Regexp(IP_ADDRESS_REGEX)), dump_only=True)

    @post_load
    def get_network_informations(self, item):
        netmask, interface = self.get_netmask_interface(item['ip_address'])
        item['interface'] = interface
        item['netmask'] = netmask
        item['gateway'] = self.get_gateway(interface)
        item['nameservers'] = self.get_nameserver()

        return item

    def get_gateway(self, interface):
        gateways = netifaces.gateways()[netifaces.AF_INET]
        for gateway in gateways:
            if interface in gateway:
                return gateway[0]
        raise Exception('Gateway not found')

    def get_netmask_interface(self, ip_address):
        for interface in netifaces.interfaces():
            addresses_ipv4 = netifaces.ifaddresses(interface)[netifaces.AF_INET]
            for address in addresses_ipv4:
                if address['addr'] == ip_address:
                    return address['netmask'], interface

        raise Exception('IP address not found')

    def get_nameserver(self):
        nameserver_regex = re.compile(NAMESERVER_REGEX)
        nameservers = []
        with open('/etc/resolv.conf', 'r') as f:
            for line in f.readlines():
                nameserver = re.match(nameserver_regex, line)
                if nameserver:
                    nameservers.append(nameserver.group(1))

        if not nameservers:
            raise Exception('Nameserver not found')

        return nameservers


class WizardSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    admin_username = fields.Constant(constant='root', dump_only=True)
    admin_password = fields.String(required=True, validate=Regexp(ADMIN_PASSWORD_REGEX))
    license = StrictBoolean(required=True, validate=Equal(True))
    language = fields.String(default='en_US', validate=OneOf(['en_US', 'fr_FR']))
    entity_name = fields.String(default='xivo', validate=Length(min=3, max=64))
    timezone = fields.String(dump_only=True, validate=Length(max=128))
    network = fields.Nested(WizardNetworkSchema)

    @post_load
    def set_timezone(self, item):
        item['timezone'] = self.get_timezone()

    def get_timezone(self):
        with open('/etc/timezone', 'r') as f:
            return f.readline().strip()


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
            raise Exception('xivo already exists')

        wizard = self.wizard_schema.load(request.get_json()).data
        wizard_with_uuid = self.service.created(wizard)
        return self.wizard_schema.dump(wizard_with_uuid).data
