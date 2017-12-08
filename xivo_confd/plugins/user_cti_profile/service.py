# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import Session

from . import validator as validator_module
from .notifier import build_notifier


class UserCTIProfileService(object):

    def __init__(self, validator, notifier):
        self.validator = validator
        self.notifier = notifier

    def edit(self, user, form):
        cti_profile_id = form.get('cti_profile_id')
        cti_enabled = form.get('cti_enabled')
        if cti_enabled is not None:
            user.cti_enabled = cti_enabled

        with Session.no_autoflush:
            self.validator.validate_edit(user, cti_profile_id)

        if 'cti_profile_id' in form:
            user.cti_profile_id = cti_profile_id

        self.notifier.edited(user)


def build_service():
    return UserCTIProfileService(validator_module,
                                 build_notifier())
