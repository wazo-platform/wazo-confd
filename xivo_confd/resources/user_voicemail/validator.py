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

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao
from xivo_dao.resources.user_voicemail import dao as user_voicemail_dao

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError
from xivo_confd.helpers.validator import Validator, AssociationValidator, \
    RequiredFields, GetResource


class UserHasNoVoicemail(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, model):
        existing = self.find(model)
        if existing:
            raise errors.resource_associated('User', 'Voicemail',
                                             user_id=model.user_id,
                                             voicemail_id=model.voicemail_id)

    def find(self, model):
        try:
            return self.dao.get_by_user_id(model.user_id)
        except NotFoundError:
            return


def build_validator():
    return AssociationValidator(
        common=[
            RequiredFields(),
            GetResource('user_id', user_dao.get, 'User'),
            GetResource('voicemail_id', voicemail_dao.get, 'Voicemail')
        ],
        association=[
            UserHasNoVoicemail(user_voicemail_dao)
        ]
    )
