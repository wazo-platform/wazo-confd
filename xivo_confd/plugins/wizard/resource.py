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

from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean

NAMESERVER_REGEX = '^nameserver (.*)'


class WizardNetworkSchema(BaseSchema):
    hostname = fields.String(required=True)
    ip_address = fields.String(required=True)
    domain = fields.String(required=True)
    interface = fields.String(dump_only=True)
    netmask = fields.String(dump_only=True)
    gateway = fields.String(dump_only=True)
    nameserver = fields.String(dump_only=True)

    @post_load
    def get_network_informations(self, item):
        netmask, interface = self.get_netmask_interface(item['ip_address'])
        item['interface'] = interface
        item['netmask'] = netmask
        item['gateway'] = self.get_gateway(interface)
        item['nameserver'] = self.get_nameserver()

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
    admin_password = fields.String(required=True)
    license = StrictBoolean(required=True)
    timezone = fields.String()
    language = fields.String()
    entity_name = fields.String()
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
            raise Exception('xivo already exists')

        wizard = self.wizard_schema.load(request.get_json()).data
        wizard_with_uuid = self.service.created(wizard)
        return self.wizard_schema.dump(wizard_with_uuid).data
