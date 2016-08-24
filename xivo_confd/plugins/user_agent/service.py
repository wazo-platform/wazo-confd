# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.resources.user import dao as user_dao

from xivo_confd.plugins.user_agent.notifier import build_notifier
from xivo_confd.plugins.user_agent.validator import build_validator


class Agent(object):
    def __init__(self, agent_id):
        self.id = agent_id


class UserAgentService(object):

    def __init__(self, dao, validator, notifier):
        self.dao = dao
        self.validator = validator
        self.notifier = notifier

    def find_by_user_id(self, user_id):
        return self.dao.find_by(id=user_id)

    def associate(self, user, agent_id):
        agent = Agent(agent_id)
        self.validator.validate_association(user, agent)
        user.agent_id = agent_id
        self.dao.edit(user)
        self.notifier.associated(user, agent)

    def dissociate(self, user):
        agent = Agent(user.agent_id)
        self.validator.validate_dissociation(user, agent)
        user.agent_id = None
        self.dao.edit(user)
        self.notifier.dissociated(user, agent)


def build_service():
    return UserAgentService(user_dao,
                            build_validator(),
                            build_notifier())
