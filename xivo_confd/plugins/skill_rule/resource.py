# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.queueskillrule import QueueSkillRule

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import SkillRuleSchema


class SkillRuleList(ListResource):

    model = QueueSkillRule
    schema = SkillRuleSchema

    def build_headers(self, skill_rule):
        return {'Location': url_for('skillrules', id=skill_rule.id, _external=True)}

    @required_acl('confd.queues.skillrules.create')
    def post(self):
        return super(SkillRuleList, self).post()

    @required_acl('confd.queues.skillrules.read')
    def get(self):
        return super(SkillRuleList, self).get()


class SkillRuleItem(ItemResource):

    schema = SkillRuleSchema
    has_tenant_uuid = True

    @required_acl('confd.queues.skillrules.{id}.read')
    def get(self, id):
        return super(SkillRuleItem, self).get(id)

    @required_acl('confd.queues.skillrules.{id}.update')
    def put(self, id):
        return super(SkillRuleItem, self).put(id)

    @required_acl('confd.queues.skillrules.{id}.delete')
    def delete(self, id):
        return super(SkillRuleItem, self).delete(id)
