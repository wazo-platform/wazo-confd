# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import assert_that, has_entries

from ..schema import CustomDestinationSchema


class TestCustomDestinationSchema(unittest.TestCase):

    def test_non_ascii_extensions(self):
        exten = '123' + u'\xa0'
        schema = CustomDestinationSchema()
        body = {'exten': exten, 'type': 'custom'}

        result = schema.load(body)

        assert_that(result, has_entries(exten='123'))
