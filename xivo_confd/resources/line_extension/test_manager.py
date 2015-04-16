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

import unittest
from mock import Mock, patch
from hamcrest import assert_that, equal_to

from xivo_dao.resources.context.model import Context
from xivo_dao.resources.user_line.model import UserLine
from xivo_dao.resources.incall.model import Incall
from xivo_dao.resources.line_extension.model import LineExtension
from xivo_dao.resources.line_extension.manager import AssociationManager
from xivo_dao.resources.line_extension.manager import IncallAssociator
from xivo_dao.resources.line_extension.manager import InternalAssociator
from xivo_dao.resources.line_extension.manager import build_manager


class TestBuildManager(unittest.TestCase):

    @patch('xivo_dao.resources.line_extension.manager.line_device_validator')
    @patch('xivo_dao.resources.line_extension.manager.extension_validator')
    @patch('xivo_dao.resources.line_extension.manager.extension_dao')
    @patch('xivo_dao.resources.line_extension.manager.incall_dao')
    @patch('xivo_dao.resources.line_extension.manager.user_line_dao')
    @patch('xivo_dao.resources.line_extension.manager.ule_services')
    @patch('xivo_dao.resources.line_extension.manager.context_dao')
    @patch('xivo_dao.resources.line_extension.manager.line_extension_validator')
    @patch('xivo_dao.resources.line_extension.manager.IncallAssociator')
    @patch('xivo_dao.resources.line_extension.manager.InternalAssociator')
    @patch('xivo_dao.resources.line_extension.manager.AssociationManager')
    def test_build_manager(self,
                           AssociationManager,
                           InternalAssociator,
                           IncallAssociator,
                           line_extension_validator,
                           context_dao,
                           ule_services,
                           user_line_dao,
                           incall_dao,
                           extension_dao,
                           extension_validator,
                           line_device_validator):

        association_manager = AssociationManager.return_value = Mock(AssociationManager)
        internal_association = InternalAssociator.return_value = Mock(InternalAssociator)
        incall_association = IncallAssociator.return_value = Mock(IncallAssociator)

        result = build_manager()

        assert_that(result, equal_to(association_manager))
        AssociationManager.assert_called_once_with(context_dao, line_extension_validator, {
            'internal': internal_association, 'incall': incall_association})

        InternalAssociator.assert_called_once_with(ule_services,
                                                   extension_validator,
                                                   line_extension_validator,
                                                   line_device_validator)
        IncallAssociator.assert_called_once_with(line_extension_validator, user_line_dao, incall_dao, extension_dao)


class TestAssociationManager(unittest.TestCase):

    def setUp(self):
        self.context_dao = Mock()
        self.validator = Mock()
        self.line_extension = Mock(LineExtension, extension_id=1)
        self.manager = AssociationManager(self.context_dao, self.validator, self.associators())


class TestGivenNoAssociators(TestAssociationManager):

    def associators(self):
        return {}

    def test_when_associating_then_raises_error(self):
        self.assertRaises(NotImplementedError, self.manager.associate, self.line_extension)

    def test_when_dissociating_then_raises_error(self):
        self.assertRaises(NotImplementedError, self.manager.associate, self.line_extension)


class TestGivenUnknownContextType(TestAssociationManager):

    def associators(self):
        self.associator = Mock()
        return {'internal': self.associator}

    def setUp(self):
        super(TestGivenUnknownContextType, self).setUp()
        self.context_dao.get_by_extension_id.return_value = Mock(Context, type='unknown')

    def test_when_associating_then_raises_error(self):
        self.assertRaises(NotImplementedError, self.manager.associate, self.line_extension)

        self.context_dao.get_by_extension_id.assert_called_once_with(self.line_extension.extension_id)

    def test_when_dissociating_then_raises_error(self):
        self.assertRaises(NotImplementedError, self.manager.dissociate, self.line_extension)

        self.context_dao.get_by_extension_id.assert_called_once_with(self.line_extension.extension_id)


class TestGivenKnownContextType(TestAssociationManager):

    def associators(self):
        self.associator = Mock()
        return {'internal': self.associator}

    def setUp(self):
        super(TestGivenKnownContextType, self).setUp()
        self.context_dao.get_by_extension_id.return_value = Mock(Context, type='internal')

    def test_when_associating_then_calls_associator(self):
        self.manager.associate(self.line_extension)

        self.associator.associate.assert_called_once_with(self.line_extension)

    def test_when_associating_then_validates_model(self):
        with patch.object(self.manager, 'validate') as mock_validate:
            self.manager.associate(self.line_extension)

            mock_validate.assert_called_once_with(self.line_extension)

    def test_when_validating_then_calls_appropriate_validators(self):
        self.manager.validate(self.line_extension)

        self.validator.validate_model.assert_called_once_with(self.line_extension)
        self.validator.validate_line.assert_called_once_with(self.line_extension)
        self.validator.validate_extension.assert_called_once_with(self.line_extension)

    def test_when_dissociating_then_calls_associator(self):
        self.manager.dissociate(self.line_extension)

        self.associator.dissociate.assert_called_once_with(self.line_extension)

    def test_when_dissociating_then_validates_models(self):
        with patch.object(self.manager, 'validate') as mock_validate:
            self.manager.dissociate(self.line_extension)

            mock_validate.assert_called_once_with(self.line_extension)

    def test_when_dissociating_then_validates_already_associated(self):
        self.manager.dissociate(self.line_extension)

        self.validator.validate_associated.assert_called_once_with(self.line_extension)


class TestInternalAssociator(unittest.TestCase):

    def setUp(self):
        self.extension_validator = Mock()
        self.line_extension_validator = Mock()
        self.line_device_validator = Mock()
        self.ule_dao = Mock()
        self.line_extension = Mock(LineExtension, line_id=12, extension_id=15)
        self.associator = InternalAssociator(self.ule_dao,
                                             self.extension_validator,
                                             self.line_extension_validator,
                                             self.line_device_validator)

    def test_when_associating_then_validates_line_not_associated_to_any_extension(self):
        self.associator.associate(self.line_extension)

        self.line_extension_validator.validate_line_not_associated_to_extension.assert_called_once_with(self.line_extension)

    def test_when_associating_then_validates_extension_not_associated(self):
        self.associator.associate(self.line_extension)

        self.extension_validator.validate_extension_not_associated.assert_called_once_with(self.line_extension.extension_id)

    def test_when_associating_then_creates_ule(self):
        self.associator.associate(self.line_extension)

        self.ule_dao.associate_line_extension.assert_called_once_with(self.line_extension)

    def test_when_dissociating_then_validates_not_associated_to_device(self):
        self.associator.dissociate(self.line_extension)

        self.line_device_validator.validate_no_device.assert_called_once_with(self.line_extension.line_id)

    def test_when_dissociating_then_deletes_ule(self):
        self.associator.dissociate(self.line_extension)

        self.ule_dao.dissociate_line_extension.assert_called_once_with(self.line_extension)


class TestIncallAssociator(unittest.TestCase):

    def setUp(self):
        self.validator = Mock()
        self.user_line_dao = Mock()
        self.incall_dao = Mock()
        self.extension_dao = Mock()
        self.line_extension = Mock(LineExtension, line_id=1, extension_id=2)
        self.associator = IncallAssociator(self.validator, self.user_line_dao, self.incall_dao, self.extension_dao)

    def test_when_associating_then_validates_association_to_user(self):
        self.associator.associate(self.line_extension)

        self.validator.validate_associated_to_user.assert_called_once_with(self.line_extension)

    def test_when_associating_then_creates_incall_with_main_user(self):
        main_user_line = self.user_line_dao.find_main_user_line.return_value = Mock(UserLine, user_id=3)
        expected_incall = Incall(destination='user',
                                 destination_id=main_user_line.user_id,
                                 extension_id=self.line_extension.extension_id)
        new_incall = self.incall_dao.create.return_value

        self.associator.associate(self.line_extension)

        self.user_line_dao.find_main_user_line.assert_called_once_with(self.line_extension.line_id)
        self.incall_dao.create.assert_called_once_with(expected_incall)
        self.extension_dao.associate_destination.assert_called_once_with(self.line_extension.extension_id,
                                                                         'incall',
                                                                         new_incall.id)

    def test_when_dissociating_then_deletes_incall(self):
        incall = self.incall_dao.find_by_extension_id.return_value = Mock(Incall)

        self.associator.dissociate(self.line_extension)

        self.incall_dao.find_by_extension_id.assert_called_once_with(self.line_extension.extension_id)
        self.incall_dao.delete.assert_called_once_with(incall)

    def test_when_dissociating_then_dissociates_extension(self):
        self.associator.dissociate(self.line_extension)

        self.extension_dao.dissociate_extension.assert_called_once_with(self.line_extension.extension_id)
