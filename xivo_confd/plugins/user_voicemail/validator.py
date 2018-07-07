# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors
from xivo_confd.helpers.validator import Validator, ValidationAssociation


class UserHasNoVoicemail(Validator):

    def validate(self, user, voicemail):
        self.validate_same_tenant(user, voicemail)
        self.validate_user_has_no_voicemail(user, voicemail)

    def validate_user_has_no_voicemail(self, user, voicemail):
        if user.voicemail:
            raise errors.resource_associated('User', 'Voicemail',
                                             user_id=user.id,
                                             voicemail_id=voicemail.id)

    def validate_same_tenant(self, user, voicemail):
        if voicemail.tenant_uuid != user.tenant_uuid:
            raise errors.different_tenants(
                voicemail_tenant_uuid=voicemail.tenant_uuid,
                user_tenant_uuid=user.tenant_uuid
            )


def build_validator():
    return ValidationAssociation(
        association=[
            UserHasNoVoicemail()
        ]
    )
