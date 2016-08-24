# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


from xivo_confd.database import agent as agent_db
from xivo_confd.helpers.validator import AssociationValidator, Validator
from xivo_dao.helpers import errors


class UserAgentAssociationValidator(Validator):

    def __init__(self, agent_db):
        self.agent_db = agent_db

    def validate(self, user, agent):
        self.validate_agent_exists(agent)
        self.validate_user_not_already_associated(user, agent)

    def validate_user_not_already_associated(self, user, agent):
        if user.agentid:
            raise errors.resource_associated('User', 'Agent',
                                             user_id=user.id, agent=agent.id)

    def validate_agent_exists(self, agent):
        exists = self.agent_db.agent_id_exists(agent.id)
        if not exists:
            raise errors.not_found('Agent', id=agent.id)


class UserAgentDissociationValidator(Validator):

    def validate(self, user, agent):
        self.validate_user_agent_exists(user)

    def validate_user_agent_exists(self, user):
        if not user.agentid:
            raise errors.not_found('UserAgent', user_id=user.id)


def build_validator():
    return AssociationValidator(
        association=[
            UserAgentAssociationValidator(agent_db)
        ],
        dissociation=[
            UserAgentDissociationValidator()
        ]
    )
