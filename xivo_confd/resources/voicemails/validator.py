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

from xivo_dao.resources.voicemail import dao as voicemail_dao
from xivo_dao.resources.language import dao as language_dao

from xivo_dao.resources.exception import NotFoundError
from xivo_dao.helpers import errors
from xivo_dao.helpers import validator


def validate_create(voicemail):
    validate_model(voicemail)
    validate_number_context(voicemail)


def validate_edit(voicemail):
    validate_model(voicemail)
    validate_existing_number_context(voicemail)
    _check_if_voicemail_associated(voicemail)


def validate_delete(voicemail):
    _check_if_voicemail_associated(voicemail)


def validate_model(voicemail):
    _check_missing_parameters(voicemail)
    _check_parameter_types(voicemail)
    _check_parameter_references(voicemail)


def _check_missing_parameters(voicemail):
    missing = voicemail.missing_parameters()
    if missing:
        raise errors.missing(*missing)


def _check_parameter_types(voicemail):
    validators = {'name': _validate_not_empty,
                  'number': _validate_number,
                  'max_messages': _validate_number,
                  'password': _validate_number,
                  'attach_audio': _validate_boolean,
                  'delete_messages': _validate_boolean,
                  'ask_pasword': _validate_boolean}

    for field_name, field_validator in validators.iteritems():
        value = getattr(voicemail, field_name, None)
        if value is not None:
            field_validator(field_name, value)


def _validate_not_empty(field_name, value):
    if value.strip() == '':
        raise errors.missing(field_name)


def _validate_number(field_name, value):
    if not validator.is_positive_number(value):
        raise errors.wrong_type(field_name, 'numeric string')


def _validate_boolean(field_name, value):
    if not isinstance(value, bool):
        raise errors.wrong_type(field_name, 'boolean')


def _check_parameter_references(voicemail):
    if not validator.is_existing_context(voicemail.context):
        raise errors.param_not_found('context', 'Context')
    if voicemail.language is not None and voicemail.language not in language_dao.find_all():
        raise errors.param_not_found('language', 'Language')
    if voicemail.timezone is not None and voicemail.timezone not in voicemail_dao.find_all_timezone():
        raise errors.param_not_found('timezone', 'Timezone')


def validate_number_context(voicemail):
    try:
        existing = voicemail_dao.get_by_number_context(voicemail.number, voicemail.context)
    except NotFoundError:
        return

    if existing:
        raise errors.resource_exists('Voicemail', number=voicemail.number, context=voicemail.context)


def validate_existing_number_context(voicemail):
    existing_voicemail = voicemail_dao.get(voicemail.id)
    if voicemail.number_at_context != existing_voicemail.number_at_context:
        validate_number_context(voicemail)


def _check_if_voicemail_associated(voicemail):
    if voicemail_dao.is_voicemail_linked(voicemail):
        raise errors.resource_associated('Voicemail', 'User')
