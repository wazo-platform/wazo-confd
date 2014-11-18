# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

import collections

from errors import ValidationError


class Field(object):

    error_message = "Input Error - field '{name}': {message}"

    def __init__(self, name, field_type, *validators, **actions):
        self.name = name
        self.field_type = field_type
        self.validators = validators
        self.actions = self._normalize_actions(actions)

    def validate(self, value, action=None):
        try:
            for validator in self._all_validators(action):
                validator(value)
        except ValidationError as e:
            raise self.reformat_error(e)

    def _all_validators(self, action):
        yield self.field_type.validate
        for validator in self.validators:
            yield validator
        for validator in self.actions.get(action, []):
            yield validator

    def reformat_error(self, error):
        msg = self.error_message.format(name=self.name, message=unicode(error))
        return ValidationError(msg)

    def _normalize_actions(self, actions):
        normalized = {}
        for action, validators in actions.items():
            if not isinstance(validators, collections.Iterable):
                validators = [validators]
            normalized[action] = validators
        return normalized
