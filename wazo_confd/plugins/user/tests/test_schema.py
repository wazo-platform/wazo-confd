# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from hamcrest import assert_that, equal_to

from ..schema import UserSchema


class TestSchema(unittest.TestCase):
    def test_flatten(self):
        user_1, user_2, user_3, user_4, user_5 = Mock(), Mock(), Mock(), Mock(), Mock()
        data_to_flatten = [
            user_1,
            [[user_2, user_3]],
            [[[user_4, [[user_5]]]]],
            [],
            [[]],
        ]
        result = list(UserSchema._flatten(data_to_flatten))
        assert_that(result, equal_to([user_1, user_2, user_3, user_4, user_5]))
