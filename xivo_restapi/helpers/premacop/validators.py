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

from errors import ValidationError


class Required(object):

    def __call__(self, value):
        if value is None:
            raise ValidationError("field is required")


class Length(object):

    def __init__(self, size=None, minimum=None, maximum=None):
        self.size = size
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, value):
        if value is None:
            return
        if self.size is not None and len(value) != self.size:
            raise ValidationError("length must be exactly {}".format(self.size))
        if self.minimum is not None and len(value) < self.minimum:
            raise ValidationError("minimum length is {}".format(self.minimum))
        if self.maximum is not None and len(value) > self.maximum:
            raise ValidationError("maximum length is {}".format(self.maximum))


class Positive(object):

    def __call__(self, value):
        if value is None:
            return
        if value <= 0:
            raise ValidationError("must be a positive number")


class Choice(object):

    def __init__(self, possibilities):
        self.possibilities = possibilities

    def __call__(self, value):
        if value is None:
            return
        if value not in self.possibilities:
            choices = ', '.join(self.possibilities)
            msg = "must be one of the following choices: {}".format(choices)
            raise ValidationError(msg)
