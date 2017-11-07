# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+


from xivo_confd.database import agent as agent_db
from xivo_confd.helpers.validator import ValidationAssociation, ValidatorAssociation
from xivo_dao.helpers import errors


class UserAgentAssociationValidator(ValidatorAssociation):

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


class UserAgentDissociationValidator(ValidatorAssociation):

    def validate(self, user, agent):
        self.validate_user_agent_exists(user)

    def validate_user_agent_exists(self, user):
        if not user.agentid:
            raise errors.not_found('UserAgent', user_id=user.id)


def build_validator():
    return ValidationAssociation(
        association=[
            UserAgentAssociationValidator(agent_db)
        ],
        dissociation=[
            UserAgentDissociationValidator()
        ]
    )
