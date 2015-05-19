# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_dao.resources.voicemail.model import Voicemail
from xivo_dao.helpers.exception import InputError
from xivo_dao.helpers.exception import ResourceError
from xivo_dao.helpers.exception import NotFoundError

from xivo_confd.resources.voicemails import validator


class TestValidateCreate(unittest.TestCase):

    @patch('xivo_confd.resources.voicemails.validator.validate_model')
    @patch('xivo_confd.resources.voicemails.validator.validate_number_context')
    def test_validate_create(self,
                             validate_model,
                             validate_number_context):

        voicemail = Mock(Voicemail)

        validator.validate_create(voicemail)

        validate_model.assert_called_once_with(voicemail)
        validate_number_context.assert_called_once_with(voicemail)


class TestValidateEdit(unittest.TestCase):

    @patch('xivo_dao.resources.voicemail.dao.is_voicemail_linked')
    @patch('xivo_confd.resources.voicemails.validator.validate_existing_number_context')
    @patch('xivo_confd.resources.voicemails.validator.validate_model')
    def test_validate_edit_not_linked(self,
                                      validate_model,
                                      validate_existing_number_context,
                                      is_voicemail_linked):
        voicemail = Mock(Voicemail, id=1, number='1000', context='default')

        is_voicemail_linked.return_value = False

        validator.validate_edit(voicemail)

        validate_model.assert_called_once_with(voicemail)
        validate_existing_number_context.assert_called_once_with(voicemail)
        is_voicemail_linked.assert_called_once_with(voicemail)

    @patch('xivo_dao.resources.voicemail.dao.is_voicemail_linked')
    @patch('xivo_confd.resources.voicemails.validator.validate_existing_number_context')
    @patch('xivo_confd.resources.voicemails.validator.validate_model')
    def test_validate_edit_when_linked(self,
                                       validate_model,
                                       validate_existing_number_context,
                                       is_voicemail_linked):
        voicemail = Mock(Voicemail, id=1, number='1000', context='default')

        is_voicemail_linked.return_value = True

        self.assertRaises(ResourceError, validator.validate_edit, voicemail)

        validate_model.assert_called_once_with(voicemail)
        validate_existing_number_context.assert_called_once_with(voicemail)
        is_voicemail_linked.assert_called_once_with(voicemail)


class TestValidateDelete(unittest.TestCase):

    @patch('xivo_dao.resources.voicemail.dao.is_voicemail_linked')
    def test_validate_delete_when_not_linked(self, is_voicemail_linked):
        voicemail = Mock(Voicemail)

        is_voicemail_linked.return_value = False

        validator.validate_delete(voicemail)

        is_voicemail_linked.assert_called_once_with(voicemail)

    @patch('xivo_dao.resources.voicemail.dao.is_voicemail_linked')
    def test_validate_delete_when_linked(self, is_voicemail_linked):
        voicemail = Mock(Voicemail)

        is_voicemail_linked.return_value = True

        self.assertRaises(ResourceError, validator.validate_delete, voicemail)

        is_voicemail_linked.assert_called_once_with(voicemail)


class TestValidateModel(unittest.TestCase):

    @patch('xivo_confd.resources.voicemails.validator.is_existing_context')
    @patch('xivo_dao.resources.voicemail.dao.find_all_timezone')
    @patch('xivo_dao.resources.language.dao.find_all')
    def test_validate_model(self, language_find_all, find_all_timezone, is_existing_context):

        languages = ['en_US']
        timezones = ['eu-fr']
        voicemail = Voicemail(name='voicemail_name',
                              number='1000',
                              context='default',
                              timezone='eu-fr',
                              language='en_US')

        language_find_all.return_value = languages
        find_all_timezone.return_value = timezones
        is_existing_context.return_value = True

        validator.validate_model(voicemail)

        language_find_all.assert_called_once_with()
        find_all_timezone.assert_called_once_with()
        is_existing_context.assert_called_once_with('default')

    def test_validate_model_empty_model(self):
        voicemail = Voicemail()

        self.assertRaises(InputError, validator.validate_model, voicemail)

    def test_validate_model_empty_name(self):
        name = ''
        number = '42'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        self.assertRaises(InputError, validator.validate_model, voicemail)

    def test_validate_model_invalid_number(self):
        name = 'voicemail'
        number = 'wrong_number'
        context = 'default'

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        self.assertRaises(InputError, validator.validate_model, voicemail)

    @patch('xivo_confd.resources.voicemails.validator.is_existing_context')
    def test_validate_model_invalid_context(self, is_existing_context):
        name = 'voicemail'
        number = '42'
        context = 'inexistant_context'

        is_existing_context.return_value = False

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context)

        self.assertRaises(InputError, validator.validate_model, voicemail)
        is_existing_context.assert_called_once_with(context)

    @patch('xivo_dao.resources.language.dao.find_all')
    @patch('xivo_confd.resources.voicemails.validator.is_existing_context')
    def test_validate_model_invalid_language(self, is_existing_context, language_dao_find_all):
        name = 'voicemail'
        number = '42'
        context = 'inexistant_context'
        language = 'zz_ZZ'

        is_existing_context.return_value = True
        language_dao_find_all.return_value = ['fr_FR']

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context,
                              language=language)

        self.assertRaises(InputError, validator.validate_model, voicemail)
        is_existing_context.assert_called_once_with(context)
        language_dao_find_all.assert_called_once_with()

    @patch('xivo_dao.resources.voicemail.dao.find_all_timezone')
    @patch('xivo_dao.resources.language.dao.find_all')
    @patch('xivo_confd.resources.voicemails.validator.is_existing_context')
    def test_validate_model_invalid_timezone(self, is_existing_context, language_dao_find_all, find_all_timezone):
        name = 'voicemail'
        number = '42'
        context = 'inexistant_context'
        language = 'zz_ZZ'

        is_existing_context.return_value = True
        language_dao_find_all.return_value = ['fr_FR']

        voicemail = Voicemail(name=name,
                              number=number,
                              context=context,
                              language=language)

        self.assertRaises(InputError, validator.validate_model, voicemail)
        is_existing_context.assert_called_once_with(context)
        language_dao_find_all.assert_called_once_with()


class TestValidateNumberContext(unittest.TestCase):

    @patch('xivo_dao.resources.voicemail.dao.get_by_number_context')
    def test_when_number_context_do_not_exist(self,
                                              get_by_number_context):
        voicemail = Voicemail(name='voicemail',
                              number='1001',
                              context='default')

        get_by_number_context.side_effect = NotFoundError

        validator.validate_number_context(voicemail)

        get_by_number_context.assert_called_once_with(voicemail.number, voicemail.context)

    @patch('xivo_dao.resources.voicemail.dao.get_by_number_context')
    def test_when_number_context_exist(self,
                                       get_by_number_context):
        existing = Voicemail(name='existing',
                             number='1001',
                             context='default')
        voicemail = Voicemail(name='voicemail',
                              number='1001',
                              context='default')

        get_by_number_context.return_value = existing

        self.assertRaises(ResourceError, validator.validate_number_context, voicemail)

        get_by_number_context.assert_called_once_with(voicemail.number, voicemail.context)


class TestValidateExistingNumberContext(unittest.TestCase):

    @patch('xivo_dao.resources.voicemail.dao.get')
    def test_when_number_context_are_same(self, voicemail_dao_get):
        voicemail_id = 1
        name = 'voicemail'
        number = '42'
        context = 'existing_context'

        voicemail = Voicemail(id=voicemail_id,
                              name=name,
                              number=number,
                              context=context)

        voicemail_dao_get.return_value = voicemail

        validator.validate_existing_number_context(voicemail)

        voicemail_dao_get.assert_called_once_with(voicemail.id)

    @patch('xivo_confd.resources.voicemails.validator.validate_number_context')
    @patch('xivo_dao.resources.voicemail.dao.get')
    def test_when_new_number_context(self,
                                     voicemail_dao_get,
                                     validate_number_context):
        exisiting_voicemail = Voicemail(name='existing_voicemail',
                                        number='1000',
                                        context='default')

        voicemail = Voicemail(name='voicemail',
                              number='1001',
                              context='default')

        voicemail_dao_get.return_value = exisiting_voicemail

        validator.validate_existing_number_context(voicemail)

        voicemail_dao_get.assert_called_once_with(voicemail.id)
        validate_number_context.assert_called_once_with(voicemail)

    @patch('xivo_dao.context_dao.get')
    def test_is_existing_context(self, mock_find):
        mock_find.return_value = Mock()

        result = validator.is_existing_context('abcd')

        mock_find.assert_called_once_with('abcd')
        assert_that(result, equal_to(True))
