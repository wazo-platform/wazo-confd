# Copyright 2019-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema


class ProvisioningNetworkingSchema(BaseSchema):
    provision_host = fields.String(attribute='net4_ip', allow_none=True)
    provision_http_port = fields.Integer(attribute='http_port')
    provision_http_base_url = fields.String(
        validate=Length(max=255), attribute='http_base_url', allow_none=True
    )
