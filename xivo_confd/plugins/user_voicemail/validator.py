# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors
from xivo_confd.helpers.validator import Validator, ValidationAssociation


class UserHasNoVoicemail(Validator):

    def validate(self, user, voicemail):
        if user.voicemail:
            raise errors.resource_associated('User', 'Voicemail',
                                             user_id=user.id,
                                             voicemail_id=voicemail.id)


def build_validator():
    return ValidationAssociation(
        association=[
            UserHasNoVoicemail()
        ]
    )
