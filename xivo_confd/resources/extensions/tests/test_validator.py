# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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

from xivo_dao.tests.test_case import TestCase

from hamcrest import assert_that, equal_to
from mock import patch, Mock

from xivo_dao.helpers.exception import InputError
from xivo_dao.helpers.exception import ResourceError

from xivo_dao.resources.extension.model import Extension
from xivo_dao.resources.context.model import ContextRange, ContextRangeType
from xivo_dao.resources.line_extension.model import LineExtension

from xivo_confd.resources.extensions import validator


class TestValidators(TestCase):

    @patch('xivo_confd.resources.extensions.validator.validate_extension_in_range')
    @patch('xivo_confd.resources.extensions.validator.validate_extension_available')
    @patch('xivo_confd.resources.extensions.validator.validate_context_exists')
    @patch('xivo_confd.resources.extensions.validator.validate_invalid_parameters')
    @patch('xivo_confd.resources.extensions.validator.validate_missing_parameters')
    def test_validate_create(self,
                             validate_missing_parameters,
                             validate_invalid_parameters,
                             validate_context_exists,
                             validate_extension_available,
                             validate_extension_in_range):

        extension = Mock()

        validator.validate_create(extension)

        validate_missing_parameters.assert_called_once_with(extension)
        validate_invalid_parameters.assert_called_once_with(extension)
        validate_context_exists.assert_called_once_with(extension)
        validate_extension_available.assert_called_once_with(extension)
        validate_extension_in_range.assert_called_once_with(extension)

    @patch('xivo_confd.resources.extensions.validator.validate_extension_in_range')
    @patch('xivo_confd.resources.extensions.validator.validate_extension_available_for_edit')
    @patch('xivo_confd.resources.extensions.validator.validate_context_exists')
    @patch('xivo_confd.resources.extensions.validator.validate_invalid_parameters')
    @patch('xivo_confd.resources.extensions.validator.validate_missing_parameters')
    def test_validate_edit(self,
                           validate_missing_parameters,
                           validate_invalid_parameters,
                           validate_context_exists,
                           validate_extension_available_for_edit,
                           validate_extension_in_range):

        extension = Mock()

        validator.validate_edit(extension)

        validate_missing_parameters.assert_called_once_with(extension)
        validate_invalid_parameters.assert_called_once_with(extension)
        validate_context_exists.assert_called_once_with(extension)
        validate_extension_available_for_edit.assert_called_once_with(extension)
        validate_extension_in_range.assert_called_once_with(extension)

    @patch('xivo_confd.resources.extensions.validator.validate_extension_not_associated')
    @patch('xivo_confd.resources.extensions.validator.validate_extension_exists')
    def test_delete(self, validate_extension_exists, validate_extension_not_associated):
        extension = Mock(Extension, id=0)

        validator.validate_delete(extension)

        validate_extension_exists.assert_called_once_with(extension)
        validate_extension_not_associated.assert_called_once_with(extension.id)


class TestValidateInvalidParameters(TestCase):

    def test_on_empty_extension_number(self):
        extension = Extension(context='toto')

        self.assertRaises(InputError, validator.validate_invalid_parameters, extension)

    def test_on_empty_context(self):
        extension = Extension(exten='1000')

        self.assertRaises(InputError, validator.validate_invalid_parameters, extension)

    def test_commented_is_not_a_boolean(self):
        extension = Extension(exten='1000', context='default', commented='lol')

        self.assertRaises(InputError, validator.validate_invalid_parameters, extension)


class TestValidateMissingParameters(TestCase):

    def test_missing_parameters_when_extension_has_no_parameters(self):
        extension = Extension()

        self.assertRaises(InputError, validator.validate_missing_parameters, extension)

    def test_missing_parameters_when_extension_has_minimal_parameters(self):
        extension = Extension(exten='1000', context='default')

        validator.validate_missing_parameters(extension)


@patch('xivo_dao.resources.context.dao.get')
class TestValidateContextExists(TestCase):

    def test_validate_context_exists_when_context_does_not_exist(self, context_get):
        context_get.return_value = None

        extension = Extension(exten='1000', context='default')

        self.assertRaises(InputError, validator.validate_context_exists, extension)

        context_get.assert_called_once_with(extension.context)

    def test_validate_context_exists_when_context_exists(self, context_get):
        context_get.return_value = Mock()

        extension = Extension(exten='1000', context='default')

        validator.validate_context_exists(extension)

        context_get.assert_called_once_with(extension.context)


@patch('xivo_dao.resources.extension.dao.find_by_exten_context')
class TestValidateExtensionAvailable(TestCase):

    def test_validate_extension_available_when_extension_does_not_exist(self, find_by_exten_context):
        find_by_exten_context.return_value = None

        extension = Extension(exten='1000', context='default')

        validator.validate_extension_available(extension)

        find_by_exten_context.assert_called_once_with(extension.exten, extension.context)

    def test_validate_extension_available_when_extension_exists(self, find_by_exten_context):
        find_by_exten_context.return_value = Mock(Extension)

        extension = Extension(exten='1000', context='default')

        self.assertRaises(ResourceError, validator.validate_extension_available, extension)

        find_by_exten_context.assert_called_once_with(extension.exten, extension.context)


@patch('xivo_confd.resources.extensions.validator.is_extension_valid_for_context')
class TestValidateExtensionInRange(TestCase):

    def test_validate_extension_in_range_when_extension_outside_of_range(self, is_extension_valid_for_context):
        is_extension_valid_for_context.return_value = False

        extension = Extension(exten='9999', context='default')

        self.assertRaises(InputError, validator.validate_extension_in_range, extension)

        is_extension_valid_for_context.assert_called_once_with(extension)

    def test_validate_extension_in_range_when_extension_inside_of_range(self, is_extension_valid_for_context):
        is_extension_valid_for_context.return_value = True

        extension = Extension(exten='1000', context='default')

        validator.validate_extension_in_range(extension)

        is_extension_valid_for_context.assert_called_once_with(extension)


class TestValidateExtensionExists(TestCase):

    @patch('xivo_dao.resources.extension.dao.get')
    def test_validate_extension_exists_when_extension_exists(self, dao_get):
        dao_get.return_value = Mock(Extension)

        extension = Mock(Extension, id=1)

        validator.validate_extension_exists(extension)

        dao_get.assert_called_once_with(extension.id)


@patch('xivo_dao.resources.line_extension.dao.find_by_extension_id')
@patch('xivo_dao.resources.extension.dao.get_type_typeval')
class TestValidateExtensionNotAssociated(TestCase):

    def test_given_extension_not_associated_then_validation_passes(self,
                                                                   get_type_typeval,
                                                                   find_by_extension_id):
        get_type_typeval.return_value = ('user', '0')
        find_by_extension_id.return_value = None
        extension_id = 1

        validator.validate_extension_not_associated(extension_id)

        get_type_typeval.assert_called_once_with(extension_id)
        find_by_extension_id.assert_called_once_with(extension_id)

    def test_given_extension_is_associated_to_a_line_then_validation_fails(self,
                                                                           get_type_typeval,
                                                                           find_by_extension_id):
        get_type_typeval.return_value = ('user', '0')
        find_by_extension_id.return_value = Mock(LineExtension, line_id=1)
        extension_id = 1

        self.assertRaises(ResourceError, validator.validate_extension_not_associated, extension_id)
        find_by_extension_id.assert_called_once_with(extension_id)

    def test_given_extension_is_associated_to_a_resource_then_validation_fails(self,
                                                                               get_type_typeval,
                                                                               find_by_extension_id):
        get_type_typeval.return_value = ('queue', '123')
        extension_id = 1

        self.assertRaises(ResourceError, validator.validate_extension_not_associated, extension_id)
        get_type_typeval.assert_called_once_with(extension_id)


class TestValidateExtensionAvailableForEdit(TestCase):

    @patch('xivo_confd.resources.extensions.validator.validate_extension_available')
    @patch('xivo_dao.resources.extension.dao.get')
    def test_when_exten_does_not_change(self, dao_get, validate_extension_available):
        dao_get.return_value = Extension(exten='1000')

        extension = Extension(id=1, exten='1000')

        validator.validate_extension_available_for_edit(extension)

        dao_get.assert_called_once_with(extension.id)
        self.assertNotCalled(validate_extension_available)

    @patch('xivo_confd.resources.extensions.validator.validate_extension_available')
    @patch('xivo_dao.resources.extension.dao.get')
    def test_when_exten_changes_but_is_available(self, dao_get, validate_extension_available):
        dao_get.return_value = Extension(exten='1000', context='default')

        extension = Extension(id=1, exten='1001', context='default')

        validator.validate_extension_available_for_edit(extension)

        dao_get.assert_called_once_with(extension.id)
        validate_extension_available.assert_called_once_with(extension)


class TestContextIsExtensionValidForContext(TestCase):

    @patch('xivo_dao.resources.context.dao.find_all_context_ranges')
    @patch('xivo_confd.resources.extensions.validator.is_extension_included_in_ranges')
    def test_is_extension_valid_for_context(self, is_extension_included_in_ranges, find_all_context_ranges):
        extension = Mock(Extension, exten='1000', context='default')

        context_ranges = find_all_context_ranges.return_value = Mock()
        is_extension_included_in_ranges.return_value = True

        result = validator.is_extension_valid_for_context(extension)

        assert_that(result, equal_to(True))
        find_all_context_ranges.assert_called_once_with(extension.context)
        is_extension_included_in_ranges.assert_called_once_with('1000', context_ranges)

    @patch('xivo_dao.resources.context.dao.find_all_context_ranges')
    def test_is_extension_valid_for_context_when_extension_is_alphanumeric(self, context_ranges):
        extension = Extension(exten='ABC123',
                              context='default')

        self.assertRaises(InputError, validator.is_extension_valid_for_context, extension)


class TestContextIsExtensionIncludedInRanges(TestCase):

    def test_when_no_ranges(self):
        expected = False

        exten = '1000'
        context_ranges = []

        result = validator.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_when_exten_is_below_minimum(self):
        expected = False

        exten = '1000'
        context_ranges = [ContextRange(start='2000', end='3000')]

        result = validator.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_when_exten_is_above_maximum(self):
        expected = False

        exten = '9999'
        context_ranges = [ContextRange(start='2000', end='3000')]

        result = validator.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_when_exten_is_same_as_minimum(self):
        expected = True

        exten = '1000'
        context_ranges = [ContextRange(start='1000', end='3000')]

        result = validator.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_when_exten_is_same_as_maximum(self):
        expected = True

        exten = '3000'
        context_ranges = [ContextRange(start='1000', end='3000')]

        result = validator.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_when_exten_is_inside_second_range(self):
        expected = True

        exten = '2000'
        context_ranges = [ContextRange(start='1000', end='1999'),
                          ContextRange(start='2000', end='2999')]

        result = validator.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_when_ranges_overlap(self):
        expected = True

        exten = '1450'
        context_ranges = [ContextRange(start='1400', end='2000'),
                          ContextRange(start='1000', end='1500')]

        result = validator.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_when_no_maximum_and_exten_is_below_minimum(self):
        expected = False

        exten = '500'
        context_ranges = [ContextRange(start='1000')]

        result = validator.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_when_no_maximum_and_exten_is_above_minimum(self):
        expected = False

        exten = '1450'
        context_ranges = [ContextRange(start='1000')]

        result = validator.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_when_no_maximum_and_exten_is_same_as_minimum(self):
        expected = True

        exten = '1000'
        context_ranges = [ContextRange(start='1000')]

        result = validator.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_when_exten_only_matches_on_a_range_with_minimum_and_maximum(self):
        expected = True

        exten = '2000'
        context_ranges = [ContextRange(start='1000'),
                          ContextRange(start='2000', end='3000')]

        result = validator.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_when_exten_only_matches_on_a_range_with_minimum(self):
        expected = True

        exten = '1000'
        context_ranges = [ContextRange(start='2000', end='3000'),
                          ContextRange(start='1000')]

        result = validator.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_when_exten_is_inside_of_range_with_did_length(self):
        expected = True

        exten = '10'
        context_ranges = [ContextRange(start='100', end='120', did_length=2)]

        result = validator.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))

    def test_when_exten_is_outside_of_range_with_did_length(self):
        expected = False

        exten = '30'
        context_ranges = [ContextRange(start='100', end='120', did_length=2)]

        result = validator.is_extension_included_in_ranges(exten, context_ranges)

        assert_that(result, equal_to(expected))


class TestContextIsExtensionValidForContextRange(TestCase):

    @patch('xivo_dao.resources.context.dao.find_all_specific_context_ranges')
    @patch('xivo_confd.resources.extensions.validator.is_extension_included_in_ranges')
    def test_is_extension_valid_for_context_range(self,
                                                  is_extension_included_in_ranges,
                                                  find_all_specific_context_ranges):
        extension = Extension(exten='1000',
                              context='default')

        context_range = find_all_specific_context_ranges.return_value = Mock()
        is_extension_included_in_ranges.return_value = True

        result = validator.is_extension_valid_for_context_range(extension, ContextRangeType.users)

        find_all_specific_context_ranges.assert_called_once_with(extension.context, ContextRangeType.users)
        is_extension_included_in_ranges.assert_called_once_with('1000', context_range)

        assert_that(result, equal_to(True))

    @patch('xivo_dao.resources.context.dao.find_all_context_ranges')
    def test_is_extension_valid_for_context_range_when_extension_is_alphanumeric(self, context_ranges):
        extension = Extension(exten='ABC123',
                              context='default')

        self.assertRaises(InputError,
                          validator.is_extension_valid_for_context_range,
                          extension,
                          ContextRangeType.users)
