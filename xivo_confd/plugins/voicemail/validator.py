# -*- coding: utf-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.helpers import errors
from xivo_dao.resources.voicemail import dao as voicemail_dao
from xivo_dao.resources.context import dao as context_dao

from xivo_confd.database import static_voicemail
from xivo_confd.helpers.validator import (GetResource,
                                          MemberOfSequence,
                                          Optional,
                                          ValidationGroup,
                                          Validator)


class NumberContextExists(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, model):
        voicemail = self.dao.find_by(number=model.number,
                                     context=model.context)
        if voicemail:
            raise errors.resource_exists('Voicemail',
                                         number=voicemail.number,
                                         context=voicemail.context)


class NumberContextChanged(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, model):
        voicemail = self.dao.find_by(number=model.number,
                                     context=model.context)
        if voicemail and voicemail.id != model.id:
            raise errors.resource_exists('Voicemail',
                                         number=voicemail.number,
                                         context=voicemail.context)


class AssociatedToUser(Validator):

    def validate(self, voicemail):
        if voicemail.users:
            user_ids = ", ".join(str(user.id) for user in voicemail.users)
            raise errors.resource_associated('Voicemail', 'User',
                                             voicemail_id=voicemail.id,
                                             user_ids=user_ids)


def build_validator():
    return ValidationGroup(
        common=[
            GetResource('context', context_dao.get_by_name, 'Context'),
            Optional('timezone', MemberOfSequence('timezone',
                                                  static_voicemail.find_all_timezone,
                                                  'Timezone')),
        ],
        create=[
            NumberContextExists(voicemail_dao)
        ],
        edit=[
            NumberContextChanged(voicemail_dao)
        ],
        delete=[
            AssociatedToUser()
        ])
