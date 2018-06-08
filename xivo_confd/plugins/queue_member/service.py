# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.queue_members import dao as queue_member_dao
from xivo_confd.plugins.queue_member.notifier import build_notifier
from xivo_confd.plugins.queue_member.validator import build_validator


class QueueMemberService(object):

    def __init__(self, dao, validator, notifier):
        self.dao = dao
        self.validator = validator
        self.notifier = notifier

    def get(self, queue_id, agent_id):
        self.validator.validate_get_agent_queue_association(queue_id, agent_id)
        return self.dao.get_by_queue_id_and_agent_id(queue_id, agent_id)

    def edit(self, queue_member):
        self.validator.validate_edit_agent_queue_association(queue_member)
        self.dao.edit_agent_queue_association(queue_member)
        self.notifier.edited(queue_member)

    def associate(self, queue_member):
        self.validator.validate_associate_agent_queue(queue_member.queue_id, queue_member.agent_id)
        qm = self.dao.associate(queue_member)
        self.notifier.associated(queue_member)
        return qm

    def dissociate(self, queue_member):
        self.validator.validate_remove_agent_from_queue(queue_member.queue_id, queue_member.agent_id)
        self.dao.remove_agent_from_queue(queue_member.agent_id, queue_member.queue_id)
        self.notifier.dissociated(queue_member)


def build_service():
    return QueueMemberService(queue_member_dao,
                              build_validator(),
                              build_notifier())
