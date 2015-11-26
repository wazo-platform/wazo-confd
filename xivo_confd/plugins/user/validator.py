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

from xivo_confd.helpers.validator import Validator, ValidationGroup, RequiredFields

from xivo_dao.helpers import errors
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.user_voicemail import dao as user_voicemail_dao


class NoVoicemailAssociated(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, user):
        user_voicemail = self.dao.find_by_user_id(user.id)
        if user_voicemail:
            raise errors.resource_associated('User',
                                             'Voicemail',
                                             user_id=user_voicemail.user_id,
                                             voicemail_id=user_voicemail.voicemail_id)


class NoLineAssociated(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, user):
        user_lines = self.dao.find_all_by_user_id(user.id)
        if user_lines:
            ids = tuple(ul.line_id for ul in user_lines)
            raise errors.resource_associated('User', 'Line', line_ids=ids)


def build_validator():
    return ValidationGroup(
        common=[
            RequiredFields('firstname'),
        ],
        delete=[
            NoVoicemailAssociated(user_voicemail_dao),
            NoLineAssociated(user_line_dao)
        ]
    )
