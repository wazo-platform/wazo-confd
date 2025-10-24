# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from marshmallow import fields
from marshmallow.validate import Equal, Length, OneOf, Regexp

from wazo_confd.helpers.mallow import BaseSchema, Nested, StrictBoolean
from wazo_confd.helpers.restful import ErrorCatchingResource

from .access_restriction import wazo_unconfigured

ADMIN_PASSWORD_REGEX = (
    r'^[a-zA-Z0-9\!\"\#\$\%\&\'\(\)\*\+\,\.\/\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\-]{4,64}$'
)
IP_ADDRESS_REGEX = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
BASE_HOSTNAME_REGEX = r'[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'
HOSTNAME_REGEX = r'^{}$'.format(BASE_HOSTNAME_REGEX)
DOMAIN_REGEX = r'^(?:{}\.)*({})$'.format(BASE_HOSTNAME_REGEX, BASE_HOSTNAME_REGEX)
INTERFACE_REGEX = r'^[\w\-\:\.]{1,64}$'


class WizardNetworkSchema(BaseSchema):
    hostname = fields.String(
        validate=(Regexp(HOSTNAME_REGEX), Length(max=63)), required=True
    )
    ip_address = fields.String(validate=Regexp(IP_ADDRESS_REGEX), required=True)
    domain = fields.String(
        validate=(Regexp(DOMAIN_REGEX), Length(max=255)), required=True
    )
    interface = fields.String(validate=Regexp(INTERFACE_REGEX), required=True)
    netmask = fields.String(validate=Regexp(IP_ADDRESS_REGEX), required=True)
    gateway = fields.String(validate=Regexp(IP_ADDRESS_REGEX), required=True)
    nameservers = fields.List(
        fields.String(validate=Regexp(IP_ADDRESS_REGEX)),
        validate=Length(max=3),
        required=True,
    )


class WizardStepsSchema(BaseSchema):
    database = fields.Boolean(load_default=True)
    manage_services = fields.Boolean(load_default=True)
    manage_hosts_file = fields.Boolean(load_default=True)
    manage_resolv_file = fields.Boolean(load_default=True)
    commonconf = fields.Boolean(load_default=True)
    provisioning = fields.Boolean(load_default=True)
    admin = fields.Boolean(load_default=True)


class WizardSchema(BaseSchema):
    xivo_uuid = fields.UUID(dump_only=True)
    admin_username = fields.Constant(constant='root', dump_only=True)
    admin_password = fields.String(validate=Regexp(ADMIN_PASSWORD_REGEX), required=True)
    license = StrictBoolean(validate=Equal(True), required=True)
    language = fields.String(validate=OneOf(['en_US', 'fr_FR']), load_default='en_US')
    timezone = fields.String(validate=Length(max=128), required=True)
    network = Nested(WizardNetworkSchema, required=True)
    steps = Nested(WizardStepsSchema, load_default=WizardStepsSchema().load({}))


class ConfiguredSchema(BaseSchema):
    configured = fields.Boolean()
    configurable = fields.Boolean()
    configurable_status = fields.Dict()


class WizardResource(ErrorCatchingResource):
    wizard_schema = WizardSchema
    configured_schema = ConfiguredSchema

    def __init__(self, service):
        self.service = service

    def get(self):
        configured = self.service.get()
        return self.configured_schema().dump(configured)

    @wazo_unconfigured
    def post(self):
        wizard = self.wizard_schema().load(request.get_json(force=True))
        wizard_with_uuid = self.service.create(wizard)
        return self.wizard_schema().dump(wizard_with_uuid)


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
    interfaces = fields.List(Nested(WizardDiscoverInterfaceSchema))
    gateways = fields.List(Nested(WizardDiscoverGatewaySchema))


class WizardDiscoverResource(ErrorCatchingResource):
    schema = WizardDiscoverSchema

    def __init__(self, service):
        self.service = service

    @wazo_unconfigured
    def get(self):
        discover = {
            'interfaces': self.service.get_interfaces(),
            'gateways': self.service.get_gateways(),
            'nameservers': self.service.get_nameservers(),
            'hostname': self.service.get_hostname(),
            'timezone': self.service.get_timezone(),
            'domain': self.service.get_domain(),
        }
        return self.schema().dump(discover)
