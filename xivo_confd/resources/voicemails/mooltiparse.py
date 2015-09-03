# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from collections import Iterable
from xivo_confd.helpers.mooltiparse.types import FieldType


class OptionType(FieldType):

    error_message = "wrong type. Should be a list of paired string tuples"

    def validate(self, options):
        if options is None:
            return
        if not isinstance(options, Iterable):
            self.raise_error(options)
        for option in options:
            self.validate_option(option)

    def validate_option(self, option):
        if not isinstance(option, Iterable):
            self.raise_error(option)
        if len(option) != 2:
            self.raise_error(option)
        for item in option:
            if not isinstance(item, (str, unicode)):
                self.raise_error(option)
