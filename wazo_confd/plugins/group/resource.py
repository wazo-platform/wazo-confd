# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import GroupSchema


class GroupList(ListResource):

    model = Group
    schema = GroupSchema

    def build_headers(self, group):
        return {'Location': url_for('groups', uuid=group.uuid, _external=True)}

    @required_acl('confd.groups.create')
    def post(self):
        return super().post()

    @required_acl('confd.groups.read')
    def get(self):
        return super().get()


class GroupItem(ItemResource):

    schema = GroupSchema
    has_tenant_uuid = True

    @required_acl('confd.groups.{uuid}.read')
    def get(self, uuid):
        return super().get(uuid)

    @required_acl('confd.groups.{uuid}.update')
    def put(self, uuid):
        return super().put(uuid)

    @required_acl('confd.groups.{uuid}.delete')
    def delete(self, uuid):
        return super().delete(uuid)
