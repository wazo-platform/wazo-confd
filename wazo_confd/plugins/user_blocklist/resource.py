# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from flask import request, url_for
from xivo_dao.alchemy.blocklist import BlocklistNumber

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ItemResource, ListResource, MeResourceMixin

from .schema import UserBlocklistNumberSchema
from .service import UserBlocklistService

logger = logging.getLogger(__name__)


class UserMeBlocklistNumberList(MeResourceMixin, ListResource):
    model = BlocklistNumber
    schema = UserBlocklistNumberSchema
    service: UserBlocklistService

    def build_headers(self, resource):
        return {
            'Location': url_for(
                'user_me_blocklist_numbers', uuid=str(resource.uuid), _external=True
            ),
        }

    @required_acl('confd.users.me.blocklist.read')
    def get(self):
        return super().get()

    def search_params(self):
        search_params = super().search_params()
        search_params['user_uuid'] = self._find_user_uuid()
        return search_params

    @required_acl('confd.users.me.blocklist.create')
    def post(self):
        form = self.schema().load(request.get_json())
        user_uuid = self._find_user_uuid()
        blocklist = self.service.get_or_create_user_blocklist(user_uuid=user_uuid)
        model = self.model(blocklist_uuid=blocklist.uuid, **form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)


class UserMeBlocklistNumberItem(MeResourceMixin, ItemResource):
    schema = UserBlocklistNumberSchema
    service: UserBlocklistService

    @required_acl('confd.users.me.blocklist.read')
    def get(self, uuid):
        kwargs = self._add_tenant_uuid()
        kwargs['user_uuid'] = self._find_user_uuid()
        model = self.service.get_by(uuid=str(uuid), **kwargs)
        return self.schema().dump(model)

    @required_acl('confd.users.me.blocklist.update')
    def put(self, uuid):
        kwargs = self._add_tenant_uuid()
        kwargs['user_uuid'] = self._find_user_uuid()
        model = self.service.get_by(uuid=str(uuid), **kwargs)
        self.parse_and_update(model)
        return '', 204

    @required_acl('confd.users.me.blocklist.delete')
    def delete(self, uuid):
        kwargs = self._add_tenant_uuid()
        kwargs['user_uuid'] = self._find_user_uuid()
        model = self.service.get_by(uuid=str(uuid), **kwargs)
        self.service.delete(model)
        return '', 204
