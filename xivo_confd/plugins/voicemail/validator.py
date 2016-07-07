# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_dao import context_dao
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers import errors
from xivo_dao.resources.voicemail import dao as voicemail_dao
from xivo_dao.resources.user_voicemail import dao as user_voicemail_dao

from xivo_confd.helpers.validator import (FindResource,
                                          MemberOfSequence,
                                          Optional,
                                          ValidationGroup,
                                          Validator)


class NumberContextExists(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, model):
        existing = self.find(model)
        if existing:
            raise errors.resource_exists('Voicemail',
                                         number=existing.number,
                                         context=existing.context)

    def find(self, model):
        try:
            return self.dao.get_by_number_context(model.number,
                                                  model.context)
        except NotFoundError:
            return None


class NumberContextChanged(NumberContextExists):

    def validate(self, model):
        existing = self.dao.get(model.id)
        if model.number_at_context != existing.number_at_context:
            super(NumberContextChanged, self).validate(model)


class AssociatedToUser(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, model):
        associations = self.dao.find_all_by_voicemail_id(model.id)
        if len(associations) > 0:
            user_ids = ", ".join(str(uv.user_id) for uv in associations)
            raise errors.resource_associated('Voicemail', 'User',
                                             voicemail_id=model.id,
                                             user_ids=user_ids)


def build_validator():
    return ValidationGroup(
        common=[
            FindResource('context', context_dao.get, 'Context'),
            Optional('timezone', MemberOfSequence('timezone',
                                                  voicemail_dao.find_all_timezone,
                                                  'Timezone')),
        ],
        create=[
            NumberContextExists(voicemail_dao)
        ],
        edit=[
            NumberContextChanged(voicemail_dao)
        ],
        delete=[
            AssociatedToUser(user_voicemail_dao)
        ])
