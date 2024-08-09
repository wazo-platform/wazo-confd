# Copyright 2022-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from wazo.tenant_flask_helpers import Tenant

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource
from wazo_confd.helpers.mallow import BaseSchema


class SubscriptionCountSchema(BaseSchema):
    id = fields.Integer(attribute='subscription_type')
    count = fields.Integer()


class UserSubscription(ConfdResource):
    schema = SubscriptionCountSchema

    def __init__(self, service):
        super().__init__()
        self.service = service

    @required_acl('confd.users.subscriptions.read')
    def get(self):
        tenant_uuid = Tenant.autodetect().uuid
        result = self.service.list(tenant_uuid)
        total = len(result)
        items = self.schema().dump(result, many=True)
        return {'total': total, 'items': items}
