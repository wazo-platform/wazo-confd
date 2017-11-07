# -*- coding: utf-8 -*-

# Copyright 2013-2016 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user_voicemail import dao as user_voicemail_dao

from xivo_confd.plugins.user_voicemail.validator import build_validator
from xivo_confd.plugins.user_voicemail import notifier


class UserVoicemailService(object):

    def __init__(self, dao, validator, notifier):
        self.dao = dao
        self.validator = validator
        self.notifier = notifier

    def get_by(self, **criteria):
        return self.dao.get_by(**criteria)

    def find_by(self, **criteria):
        return self.dao.find_by(**criteria)

    def find_all_by(self, **criteria):
        return self.dao.find_all_by(**criteria)

    def associate(self, user, voicemail):
        self.validator.validate_association(user, voicemail)
        self.dao.associate(user, voicemail)
        self.notifier.associated(user, voicemail)
        return self.dao.get_by(user_id=user.id)

    def dissociate(self, user, voicemail):
        self.validator.validate_dissociation(user, voicemail)
        self.dao.dissociate(user, voicemail)
        self.notifier.dissociated(user, voicemail)


def build_service():
    validator = build_validator()
    return UserVoicemailService(user_voicemail_dao,
                                validator,
                                notifier)
