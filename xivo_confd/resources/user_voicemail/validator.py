# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_dao.resources import errors
from xivo_dao.resources.exception import NotFoundError

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.user_voicemail import dao as user_voicemail_dao
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao


def validate_association(user_voicemail):
    _validate_missing_parameters(user_voicemail)
    _validate_invalid_parameters(user_voicemail)
    _validate_user_id(user_voicemail)
    _validate_voicemail_id(user_voicemail)
    _validate_user_has_line(user_voicemail)
    _validate_user_does_not_have_a_voicemail(user_voicemail)


def _validate_missing_parameters(user_voicemail):
    missing = user_voicemail.missing_parameters()
    if len(missing) > 0:
        raise errors.missing(*missing)


def _validate_invalid_parameters(user_voicemail):
    if not isinstance(user_voicemail.enabled, bool):
        raise errors.wrong_type('enabled', 'boolean', enabled=user_voicemail.enabled)


def _validate_user_id(user_voicemail):
    try:
        return user_dao.get(user_voicemail.user_id)
    except NotFoundError:
        raise errors.param_not_found('user_id', 'User')


def _validate_voicemail_id(user_voicemail):
    try:
        return voicemail_dao.get(user_voicemail.voicemail_id)
    except NotFoundError:
        raise errors.param_not_found('voicemail_id', 'Voicemail')


def _validate_user_has_line(user_voicemail):
    user_lines = user_line_dao.find_all_by_user_id(user_voicemail.user_id)
    if len(user_lines) == 0:
        raise errors.missing_association('User', 'Line', user_id=user_voicemail.user_id)


def _validate_user_does_not_have_a_voicemail(user_voicemail):
    try:
        user_voicemail_dao.get_by_user_id(user_voicemail.user_id)
    except NotFoundError:
        return

    raise errors.resource_associated('User', 'Voicemail',
                                     user_id=user_voicemail.user_id,
                                     voicemail_id=user_voicemail.voicemail_id)


def validate_dissociation(user_voicemail):
    _validate_user_id(user_voicemail)
    _validate_voicemail_id(user_voicemail)
