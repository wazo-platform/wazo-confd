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
from hamcrest import assert_that, raises, calling
from mock import Mock, sentinel

from xivo_dao.helpers.new_model import NewModel
from xivo_dao.helpers.exception import InputError, NotFoundError

from xivo_confd.helpers.validator import RequiredValidator, ResourceGetValidator, \
    ResourceExistValidator


class TestRequiredValidator(unittest.TestCase):

    def setUp(self):
        self.validator = RequiredValidator()

    def test_given_missing_fields_when_validating_then_raises_error(self):
        model = Mock(NewModel)
        model.missing_parameters.return_value = ['foobar']

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(InputError))

    def test_given_no_missing_fields_when_validating_then_passes(self):
        model = Mock(NewModel)
        model.missing_parameters.return_value = []

        self.validator.validate(model)


class TestResourceGetValidator(unittest.TestCase):

    def setUp(self):
        self.dao_get = Mock()
        self.validator = ResourceGetValidator('field', self.dao_get)

    def test_given_resource_does_not_exist_then_raises_error(self):
        model = Mock(field=sentinel.field)

        self.dao_get.side_effect = NotFoundError

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(InputError))

    def test_given_resource_exists_then_validation_passes(self):
        model = Mock(field=sentinel.field)

        self.validator.validate(model)

        self.dao_get.assert_called_once_with(model.field)


class TestResourceExistValidator(unittest.TestCase):

    def setUp(self):
        self.dao_exist = Mock()
        self.validator = ResourceExistValidator('field', self.dao_exist)

    def test_given_resource_does_not_exist_then_raises_error(self):
        model = Mock(field=sentinel.field)

        self.dao_exist.return_value = False

        assert_that(calling(self.validator.validate).with_args(model),
                    raises(InputError))

    def test_given_resource_exists_then_validation_passes(self):
        model = Mock(field=sentinel.field)

        self.dao_exist.return_value = True

        self.validator.validate(model)

        self.dao_exist.assert_called_once_with(model.field)
