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

from hamcrest import assert_that, equal_to
from mock import patch, Mock

from xivo_dao.data_handler.exception import NonexistentParametersError, AssociationNotExistsError
from xivo_restapi.resources.line_extension_collection import actions

LINE_ID = 1
EXTENSION_ID = 2


@patch('xivo_restapi.resources.line_extension_collection.actions.formatter')
class TestLineExtensionCollectionActions(unittest.TestCase):

    @patch('xivo_dao.data_handler.line_extension.services.get_all_by_line_id')
    def test_list_extensions(self, get_all_by_line_id, formatter):
        model_list = get_all_by_line_id.return_value = [Mock()]
        formatted_list = formatter.list_to_api.return_value = Mock()

        result = actions.list_extensions(LINE_ID)

        get_all_by_line_id.assert_called_once_with(LINE_ID)
        formatter.list_to_api.assert_called_once_with(model_list)
        assert_that(result, equal_to(formatted_list))

    @patch('xivo_dao.data_handler.line_extension.services.associate')
    def test_associate_extension(self, associate, formatter):
        model = formatter.to_model.return_value = Mock()
        created_model = associate.return_value = Mock()
        formatted_model = formatter.to_api.return_value = Mock()
        parameters = Mock()

        result = actions.associate_extension(LINE_ID, parameters)

        formatter.to_model.assert_called_once_with(LINE_ID, parameters)
        associate.assert_called_once_with(model)
        formatter.to_api.assert_callled_once_with(created_model)
        assert_that(result, equal_to(formatted_model))

    @patch('xivo_dao.data_handler.line_extension.services.dissociate')
    def test_dissociate_extension(self, dissociate, formatter):
        model = formatter.model_from_ids.return_value = Mock()

        result = actions.dissociate_extension(LINE_ID, EXTENSION_ID)

        dissociate.assert_called_once_with(model)
        formatter.model_from_ids.assert_callled_once_with(LINE_ID, EXTENSION_ID)
        assert_that(result, equal_to(''))

    @patch('xivo_dao.data_handler.line_extension.services.dissociate')
    def test_dissociate_extension_when_ids_do_not_exist(self, dissociate, formatter):
        dissociate.side_effect = NonexistentParametersError()
        model = formatter.model_from_ids.return_value = Mock()

        self.assertRaises(AssociationNotExistsError,
                          actions.dissociate_extension,
                          LINE_ID, EXTENSION_ID)

        dissociate.assert_called_once_with(model)
        formatter.model_from_ids.assert_callled_once_with(LINE_ID, EXTENSION_ID)
