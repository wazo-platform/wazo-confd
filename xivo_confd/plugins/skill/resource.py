# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.queueskill import QueueSkill

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import SkillSchema


class SkillList(ListResource):

    model = QueueSkill
    schema = SkillSchema

    def build_headers(self, skill):
        return {'Location': url_for('skills', id=skill.id, _external=True)}

    @required_acl('confd.agents.skills.create')
    def post(self):
        return super(SkillList, self).post()

    @required_acl('confd.agents.skills.read')
    def get(self):
        return super(SkillList, self).get()


class SkillItem(ItemResource):

    schema = SkillSchema
    has_tenant_uuid = True

    @required_acl('confd.agents.skills.{id}.read')
    def get(self, id):
        return super(SkillItem, self).get(id)

    @required_acl('confd.agents.skills.{id}.update')
    def put(self, id):
        return super(SkillItem, self).put(id)

    @required_acl('confd.agents.skills.{id}.delete')
    def delete(self, id):
        return super(SkillItem, self).delete(id)
