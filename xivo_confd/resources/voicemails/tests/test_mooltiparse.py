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

import unittest

from xivo_confd.helpers.mooltiparse.errors import ValidationError
from xivo_confd.resources.voicemails.mooltiparse import OptionType


class TestOptionType(unittest.TestCase):

    def setUp(self):
        self.opttype = OptionType()

    def test_when_options_is_null_then_validation_passes(self):
        self.opttype.validate(None)

    def test_when_options_is_empty_then_validation_passes(self):
        self.opttype.validate([])

    def test_when_options_is_not_a_list_then_validation_fails(self):
        self.assertRaises(ValidationError,
                          self.opttype.validate,
                          'options')

    def test_when_options_is_a_one_dimension_array_then_validation_fails(self):
        self.assertRaises(ValidationError,
                          self.opttype.validate,
                          ['option1', 'option2', 'option3'])

    def test_when_items_in_options_are_not_pairs_then_validation_fails(self):
        self.assertRaises(ValidationError,
                          self.opttype.validate,
                          [['option1', 'option2', 'option3']])

    def test_when_an_option_pair_are_not_strings_then_validation_fails(self):
        self.assertRaises(ValidationError,
                          self.opttype.validate,
                          [['option', 1]])

    def test_when_option_items_are_pairs_of_strings_then_validation_passes(self):
        self.opttype.validate([['option1', 'value1'],
                               ['option2', 'value2']])
