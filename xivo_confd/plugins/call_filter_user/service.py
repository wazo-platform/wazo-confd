# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.call_filter import dao as call_filter_dao_module

from .notifier import build_notifier
from .validator import (
    build_validator_recipient_user,
    build_validator_surrogate_user,
)


class CallFilterUserService:

    def __init__(self, call_filter_dao, notifier, validator_recipient_user, validator_surrogate_user):
        self.call_filter_dao = call_filter_dao
        self.notifier = notifier
        self.validator_recipient_user = validator_recipient_user
        self.validator_surrogate_user = validator_surrogate_user

    def find_recipient_by_user(self, call_filter, user):
        for recipient in call_filter.recipients:
            if user == recipient.user:
                return recipient

    def find_surrogate_by_user(self, call_filter, user):
        for surrogate in call_filter.surrogates:
            if user == surrogate.user:
                return surrogate

    def associate_recipients(self, call_filter, recipients):
        users = [recipient.user for recipient in recipients]
        self.validator_recipient_user.validate_association(call_filter, users)
        self.call_filter_dao.associate_recipients(call_filter, recipients)
        self.notifier.recipient_users_associated(call_filter, users)

    def associate_surrogates(self, call_filter, surrogates):
        users = [surrogate.user for surrogate in surrogates]
        self.validator_surrogate_user.validate_association(call_filter, users)
        self.call_filter_dao.associate_surrogates(call_filter, surrogates)
        self.notifier.surrogate_users_associated(call_filter, users)


def build_service():
    return CallFilterUserService(
        call_filter_dao_module,
        build_notifier(),
        build_validator_recipient_user(),
        build_validator_surrogate_user(),
    )
