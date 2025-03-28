# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from flask import url_for, request

from xivo_dao.alchemy.blocklist import BlocklistNumber

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource, MeResourceMixin

from .schema import (
    UserBlocklistNumberSchema,
)
from .service import UserBlocklistService

logger = logging.getLogger(__name__)


class UserBlocklistNumberList(MeResourceMixin, ListResource):
    model = BlocklistNumber
    schema = UserBlocklistNumberSchema
    service: UserBlocklistService

    def build_headers(self, resource):
        return {
            'Location': url_for(
                'user_blocklist_numbers', uuid=str(resource.uuid), _external=True
            ),
        }

    @required_acl('confd.users.me.blocklist.read')
    def get(self):
        return super().get()

    @required_acl('confd.users.me.blocklist.create')
    def post(self):
        form = self.schema().load(request.get_json())
        user_uuid = self._find_user_uuid()
        blocklist = self.service.get_or_create_user_blocklist(user_uuid=user_uuid)
        model = self.model(blocklist_uuid=blocklist.uuid, **form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)


class UserBlocklistNumberItem(ItemResource):
    schema = UserBlocklistNumberSchema

    @required_acl('confd.users.me.blocklist.read')
    def get(self, uuid):
        return super().get(str(uuid))

    @required_acl('confd.users.me.blocklist.update')
    def put(self, uuid):
        return super().put(str(uuid))

    @required_acl('confd.users.me.blocklist.delete')
    def delete(self, uuid):
        return super().delete(str(uuid))
