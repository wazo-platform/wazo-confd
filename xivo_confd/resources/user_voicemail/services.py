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

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao
from xivo_dao.resources.user_voicemail import dao as user_voicemail_dao

from xivo_confd.resources.user_voicemail.validator import build_validator
from xivo_confd.resources.user_voicemail import notifier


class UserVoicemailService(object):

    def __init__(self, user_dao, voicemail_dao, user_voicemail_dao, validator, notifier):
        self.user_dao = user_dao
        self.voicemail_dao = voicemail_dao
        self.user_voicemail_dao = user_voicemail_dao
        self.validator = validator
        self.notifier = notifier

    def validate_parent(self, user_id):
        self.user_dao.get(user_id)

    def validate_resource(self, voicemail_id):
        self.voicemail_dao.get(voicemail_id)

    def get_by_parent(self, user_id):
        return self.user_voicemail_dao.get_by_user_id(user_id)

    def list_by_child(self, voicemail_id):
        return self.user_voicemail_dao.find_all_by_voicemail_id(voicemail_id)

    def find_by(self, **criteria):
        return self.user_voicemail_dao.find_by(**criteria)

    def associate(self, association):
        self.validator.validate_association(association)
        self.user_voicemail_dao.associate(association)
        self.notifier.associated(association)
        return association

    def associate_models(self, user, voicemail):
        association = UserVoicemail(user_id=user.id,
                                    voicemail_id=voicemail.id)
        return self.associate(association)

    def dissociate(self, association):
        self.validator.validate_dissociation(association)
        self.user_voicemail_dao.dissociate(association)
        self.notifier.dissociated(association)

    def dissociate_models(self, user, voicemail):
        association = UserVoicemail(user_id=user.id,
                                    voicemail_id=voicemail.id)
        return self.dissociate(association)


def build_service():
    validator = build_validator()
    return UserVoicemailService(user_dao,
                                voicemail_dao,
                                user_voicemail_dao,
                                validator,
                                notifier)
