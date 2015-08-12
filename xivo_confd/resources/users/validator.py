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
import re

from xivo_dao.helpers import errors
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.user_voicemail import dao as user_voicemail_dao


MOBILE_PHONE_NUMBER_REGEX = re.compile(r"^\+?[0-9\*#]+$")
CALLER_ID_REGEX = re.compile(r'^"(.*)"( <\+?\d+>)?$')


def validate_create(user):
    validate_model(user)
    validate_private_template_id_is_not_set(user)
    validate_caller_id(user, required=False)


def validate_edit(user):
    validate_model(user)
    validate_private_template_id_does_not_change(user)
    validate_caller_id(user, required=True)


def validate_delete(user):
    validate_user_exists(user)
    validate_user_not_associated(user)


def validate_model(user):
    _check_missing_parameters(user)
    _check_invalid_parameters(user)


def _check_missing_parameters(user):
    missing = user.missing_parameters()
    if missing:
        raise errors.missing(*missing)


def _check_invalid_parameters(user):
    if not user.firstname:
        raise errors.missing('firstname')
    if user.mobile_phone_number and not MOBILE_PHONE_NUMBER_REGEX.match(user.mobile_phone_number):
        raise errors.wrong_type('mobile_phone_number', 'numeric phone number')
    if user.password is not None and len(user.password) < 4:
        raise errors.minimum_length('password', 4)


def validate_caller_id(user, required=False):
    if user.caller_id:
        if not CALLER_ID_REGEX.match(user.caller_id):
            raise errors.wrong_type('caller_id', 'formatted caller id string')
    elif required:
        raise errors.missing('caller_id')


def validate_user_not_associated(user):
    validate_not_associated_to_voicemail(user)
    validate_not_associated_to_line(user)


def validate_not_associated_to_line(user):
    user_lines = user_line_dao.find_all_by_user_id(user.id)
    if user_lines:
        ids = tuple(ul.line_id for ul in user_lines)
        raise errors.resource_associated('User', 'Line', line_ids=ids)


def validate_user_exists(user):
    user_dao.get(user.id)


def validate_not_associated_to_voicemail(user):
    user_voicemail = user_voicemail_dao.find_by_user_id(user.id)
    if user_voicemail:
        raise errors.resource_associated('User',
                                         'Voicemail',
                                         user_id=user_voicemail.user_id,
                                         voicemail_id=user_voicemail.voicemail_id)


def validate_private_template_id_is_not_set(user):
    if user.private_template_id:
        raise errors.unknown('private_template_id')


def validate_private_template_id_does_not_change(user):
    existing_user = user_dao.get(user.id)
    if user.private_template_id != existing_user.private_template_id:
        raise errors.unknown('private_template_id')
