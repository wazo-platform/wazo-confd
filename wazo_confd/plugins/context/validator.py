# Copyright (C) 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.extension import dao as extension_dao_module
from xivo_dao.resources.sip_general import dao as sip_general_dao_module
from xivo_dao.resources.trunk import dao as trunk_dao_module
from xivo_dao.resources.voicemail import dao as voicemail_dao_module

from xivo_confd.helpers.validator import (
    UniqueField,
    Validator,
    ValidationGroup,
)
from xivo_confd.database import agent_status_login as agent_login_status_dao_module


class ContextDeleteValidator(Validator):

    def __init__(self, agent_login_status_dao, extension_dao, sip_general_dao, trunk_dao, voicemail_dao):
        self.agent_login_status_dao = agent_login_status_dao
        self.extension_dao = extension_dao
        self.sip_general_dao = sip_general_dao
        self.trunk_dao = trunk_dao
        self.voicemail_dao = voicemail_dao

    def validate(self, context):
        self.validate_has_no_extensions(context)
        self.validate_has_no_voicemails(context)
        self.validate_has_no_trunks(context)
        self.validate_has_no_agent_status(context)
        self.validate_has_no_sip_general(context)

    def validate_has_no_extensions(self, context):
        extension = self.extension_dao.find_by(context=context.name)
        if extension:
            raise errors.resource_associated('Context', 'Extension',
                                             context_id=context.id,
                                             extension_id=extension.id)

    def validate_has_no_voicemails(self, context):
        voicemail = self.voicemail_dao.find_by(context=context.name)
        if voicemail:
            raise errors.resource_associated('Context', 'Voicemail',
                                             context_id=context.id,
                                             voicemail_id=voicemail.id)

    def validate_has_no_trunks(self, context):
        trunk = self.trunk_dao.find_by(context=context.name)
        if trunk:
            raise errors.resource_associated('Context', 'Trunk',
                                             context_id=context.id,
                                             trunk_id=trunk.id)

    def validate_has_no_agent_status(self, context):
        agent_status = self.agent_login_status_dao.find_by(context=context.name)
        if agent_status:
            raise errors.resource_associated('Context', 'AgentLoginStatus',
                                             context_id=context.id,
                                             agent_id=agent_status.agent_id)

    def validate_has_no_sip_general(self, context):
        sip_general_option = self.sip_general_dao.find_by(var_name='context', var_val=context.name)
        if sip_general_option:
            raise errors.resource_associated('Context', 'SIP General',
                                             context_id=context.id,
                                             sip_general_option='context')


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField('name',
                        lambda name: context_dao.find_by(name=name),
                        'Context'),
        ],
        delete=[ContextDeleteValidator(agent_login_status_dao_module,
                                       extension_dao_module,
                                       sip_general_dao_module,
                                       trunk_dao_module,
                                       voicemail_dao_module)]
    )
