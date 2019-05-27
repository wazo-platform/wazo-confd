# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import assert_that, calling, equal_to, raises
from werkzeug.routing import ValidationError

from xivo_confd.helpers.converter import FilenameConverter


class TestFilenameConverter(unittest.TestCase):

    def setUp(self):
        self.converter = FilenameConverter(None)

    def test_valid_filenames(self):
        values = [
            'foo',
            'foo.wav',
            'foé.txt',
            'foo.bar.-!3_X!".lol',
        ]
        for value in values:
            assert_that(self.converter.to_python(value), equal_to(value))

    def test_invalid_filenames(self):
        values = [
            '',
            '.',
            '.foo',
            '..',
            '../foo',
            'foo/bar',
        ]
        for value in values:
            assert_that(calling(self.converter.to_python).with_args(value),
                        raises(ValidationError))
