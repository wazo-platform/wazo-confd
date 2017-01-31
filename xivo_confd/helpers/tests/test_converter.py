# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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

import unittest

from hamcrest import assert_that, calling, equal_to, raises
from werkzeug.routing import ValidationError

from xivo_confd.helpers.converter import FilenameConverter


class TestFilenameConverter(unittest.TestCase):

    def setUp(self):
        self.converter = FilenameConverter(None)

    def test_valid_filenames(self):
        values = [
            u'foo',
            u'foo.wav',
            u'foé.txt',
            u'foo.bar.-!3_X!".lol',
        ]
        for value in values:
            assert_that(self.converter.to_python(value), equal_to(value))

    def test_invalid_filenames(self):
        values = [
            u'',
            u'.',
            u'.foo',
            u'..',
            u'../foo',
            u'foo/bar',
        ]
        for value in values:
            assert_that(calling(self.converter.to_python).with_args(value),
                        raises(ValidationError))
