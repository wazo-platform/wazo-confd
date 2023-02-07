# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from uuid import uuid4

from flask import url_for, request

from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import GroupSchema


class GroupList(ListResource):
    model = Group
    schema = GroupSchema
    group_name_fmt = 'grp-{tenant_slug}-{group_uuid}'

    def __init__(self, tenant_dao, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tenant_dao = tenant_dao

    def build_headers(self, group):
        return {'Location': url_for('groups', uuid=group.uuid, _external=True)}

    @required_acl('confd.groups.create')
    def post(self):
        form = self.schema().load(request.get_json())
        form = self.add_tenant_to_form(form)

        tenant = self._tenant_dao.get(form['tenant_uuid'])
        form['uuid'] = uuid4()
        form['name'] = self.group_name_fmt.format(
            tenant_slug=tenant.slug,
            group_uuid=form['uuid'],
        )

        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)

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
