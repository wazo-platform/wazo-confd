# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_dao.resources.user_voicemail.model import UserVoicemail

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
        association = UserVoicemail(user_id=user.id,
                                    voicemail_id=voicemail.id)
        self.validator.validate_association(association)
        self.dao.associate(association)
        self.notifier.associated(association)
        return association

    def dissociate(self, user, voicemail):
        association = UserVoicemail(user_id=user.id,
                                    voicemail_id=voicemail.id)
        self.validator.validate_dissociation(association)
        self.dao.dissociate(association)
        self.notifier.dissociated(association)


def build_service():
    validator = build_validator()
    return UserVoicemailService(user_voicemail_dao,
                                validator,
                                notifier)
