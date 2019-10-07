# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from wazo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class QueueMemberUserAssociationValidator(ValidatorAssociation):
    def validate(self, queue, member):
        self.validate_same_tenant(queue, member.user)
        self.validate_user_has_endpoint(member.user)
        self.validate_no_users_have_same_line(queue, member.user)

    def validate_user_has_endpoint(self, user):
        if not user.lines:
            raise errors.missing_association('User', 'Line', user_uuid=user.uuid)

    def validate_no_users_have_same_line(self, queue, user):
        all_lines = [member.user.lines[0] for member in queue.user_queue_members]
        if user.lines[0] in all_lines:
            raise errors.not_permitted(
                'Cannot associate different users with the same line',
                line_id=user.lines[0].id,
            )

    def validate_same_tenant(self, queue, user):
        if queue.tenant_uuid != user.tenant_uuid:
            raise errors.different_tenants(
                queue_tenant_uuid=queue.tenant_uuid, user_tenant_uuid=user.tenant_uuid
            )


class QueueMemberAgentAssociationValidator(ValidatorAssociation):
    def validate(self, queue, member):
        self.validate_same_tenant(queue, member.agent)

    def validate_same_tenant(self, queue, agent):
        if queue.tenant_uuid != agent.tenant_uuid:
            raise errors.different_tenants(
                queue_tenant_uuid=queue.tenant_uuid, agent_tenant_uuid=agent.tenant_uuid
            )


def build_validator_member_user():
    return ValidationAssociation(association=[QueueMemberUserAssociationValidator()])


def build_validator_member_agent():
    return ValidationAssociation(association=[QueueMemberAgentAssociationValidator()])
