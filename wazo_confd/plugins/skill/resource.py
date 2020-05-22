# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.queueskill import QueueSkill

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import SkillSchema


class SkillList(ListResource):

    model = QueueSkill
    schema = SkillSchema

    def build_headers(self, skill):
        return {'Location': url_for('skills', id=skill.id, _external=True)}

    @required_acl('confd.agents.skills.create')
    def post(self):
        return super().post()

    @required_acl('confd.agents.skills.read')
    def get(self):
        return super().get()


class SkillItem(ItemResource):

    schema = SkillSchema
    has_tenant_uuid = True

    @required_acl('confd.agents.skills.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.agents.skills.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.agents.skills.{id}.delete')
    def delete(self, id):
        return super().delete(id)
