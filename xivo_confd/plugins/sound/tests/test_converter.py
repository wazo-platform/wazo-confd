# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import (
    assert_that,
    equal_to,
)

from ..converter import ExtensionFormatConverter as EFConverter


class TestExtensionFormatConverter(unittest.TestCase):

    def test_extension_to_format_with_None(self):
        result = EFConverter.extension_to_format('')
        assert_that(result, equal_to(None))

    def test_extension_to_format_with_wav(self):
        result = EFConverter.extension_to_format('wav')
        assert_that(result, equal_to('slin'))

    def test_extension_to_format_with_other(self):
        result = EFConverter.extension_to_format('other_extension')
        assert_that(result, equal_to('other_extension'))

    def test_format_to_extension_with_None(self):
        result = EFConverter.format_to_extension(None)
        assert_that(result, equal_to(''))

    def test_format_to_extension_with_wav(self):
        result = EFConverter.format_to_extension('slin')
        assert_that(result, equal_to('wav'))

    def test_format_to_extension_with_other(self):
        result = EFConverter.format_to_extension('other_extension')
        assert_that(result, equal_to('other_extension'))
