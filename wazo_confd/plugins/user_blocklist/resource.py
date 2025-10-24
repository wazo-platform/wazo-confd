# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from flask import request, url_for
from xivo_dao.alchemy.blocklist import BlocklistNumber
from xivo_dao.helpers.exception import NotFoundError

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ItemResource, ListResource, MeResourceMixin

from .schema import (
    BlocklistNumberSchema,
    UserBlocklistNumberSchema,
    blocklist_number_list_schema,
    user_blocklist_lookup_schema,
)
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
        form = self.schema().load(request.get_json(force=True))
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


class UserBlocklistNumberList(ListResource):
    model = BlocklistNumber
    schema = BlocklistNumberSchema
    service: UserBlocklistService
    has_tenant_uuid = True

    def build_headers(self, model: BlocklistNumber):
        return {
            'Location': url_for(
                'user_blocklist_numbers', uuid=str(model.uuid), _external=True
            ),
            'Wazo-Blocklist-Number-UUID': str(model.uuid),
            'Wazo-Blocklist-Number-Label': model.label or '',
        }

    @required_acl('confd.users.{user_uuid}.blocklist.read')
    def head(self, user_uuid):
        params = user_blocklist_lookup_schema.load(request.args)
        logger.debug('lookup params: %s', params)
        tenant_uuids = self._build_tenant_list(params)
        try:
            match = self.service.get_by(
                user_uuid=str(user_uuid),
                number=params.get('number_exact'),
                tenant_uuids=tenant_uuids,
            )
        except NotFoundError:
            return '', 404
        return ('', 204, self.build_headers(match))

    @required_acl('confd.users.{user_uuid}.blocklist.read')
    def get(self, user_uuid):
        params = self.search_params()
        tenant_uuids = self._build_tenant_list(params)

        logger.debug('blocklist search params: %s', params)
        logger.debug('tenant_uuids: %s', tenant_uuids)
        params['user_uuid'] = str(user_uuid)

        total, items = self.service.search(params, tenant_uuids=tenant_uuids)
        return {'total': total, 'items': self.schema().dump(items, many=True)}


class BlocklistNumberList(ListResource):
    model = BlocklistNumber
    schema = BlocklistNumberSchema
    service: UserBlocklistService
    has_tenant_uuid = True

    @required_acl('confd.users.blocklist.read')
    def get(self):
        params = self.search_params()
        tenant_uuids = self._build_tenant_list(params)

        logger.debug('blocklist search params: %s', params)
        logger.debug('tenant_uuids: %s', tenant_uuids)
        total, items = self.service.search(params, tenant_uuids=tenant_uuids)
        return {'total': total, 'items': self.schema().dump(items, many=True)}

    def search_params(self):
        params = blocklist_number_list_schema.load(request.args)
        return params


class BlocklistNumberItem(ItemResource):
    has_tenant_uuid = True
    model = BlocklistNumber
    schema = BlocklistNumberSchema
    service: UserBlocklistService

    @required_acl('confd.users.blocklist.read')
    def get(self, uuid):
        kwargs = self._add_tenant_uuid()
        model = self.service.get_by(uuid=str(uuid), **kwargs)
        return self.schema().dump(model)
