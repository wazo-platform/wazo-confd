# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, sentinel

from xivo_dao.helpers.exception import ResourceError

from ..validator import UserEntityAssociationValidator


class TestValidateNoLineAssociated(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = UserEntityAssociationValidator(self.dao)

    def test_given_line_associated_then_validation_fails(self):
        user = Mock(id=sentinel.id)
        self.dao.find_all_by.return_value = [Mock(line_id=sentinel.line_id)]

        self.assertRaises(ResourceError, self.validator.validate_user_no_line_associated, user)

        self.dao.find_all_by.assert_called_once_with(user_id=user.id)

    def test_given_no_line_associated_then_validation_passes(self):
        user = Mock(id=sentinel.id)
        self.dao.find_all_by.return_value = []

        self.validator.validate_user_no_line_associated(user)

        self.dao.find_all_by.assert_called_once_with(user_id=user.id)
