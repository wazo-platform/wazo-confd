# -*- coding: UTF-8 -*-
#
# Copyright (C) 2013 Avencall
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
import json

from mock import Mock, patch
from hamcrest import assert_that, equal_to, all_of, has_property

from xivo_restapi.helpers import serializer
from xivo_restapi.helpers.formatter import Formatter
from xivo_dao.helpers.abstract_model import AbstractModels


class TestFormatter(unittest.TestCase):

    def setUp(self):
        self._api_data_dict = {
            'api_key_1': 1,
            'api_key_2': '2',
            'api_key_3': [1, '2']
        }
        self._model_data_dict = {
            'model_key_1': 1,
            'model_key_2': '2',
            'model_key_3': [1, '2']
        }

        self._mapper = Mock()
        self._mapper.MAPPING = {
            'model_key_1': 'api_key_1',
            'model_key_2': 'api_key_2',
            'model_key_3': 'api_key_3'
        }
        self._mapper.add_links_to_dict = Mock()
        self._mapper.add_links_to_dict.side_effect = self.add_links_to_dict

        self._serializer = Mock(serializer)
        self._serializer.decode.side_effect = json.loads
        self._serializer.encode.side_effect = json.dumps

        self.model = Mock(
            model_key_1=1,
            model_key_2='2',
            model_key_3=[1, '2']
        )
        self.model.to_data_dict.return_value = self._model_data_dict

        self._model_class = Mock(AbstractModels)
        self._model_class.from_user_data.return_value = self.model

        self.formatter = Formatter(self._mapper,
                                   self._serializer,
                                   self._model_class)

    def add_links_to_dict(self, data_dict, obj):
        data_dict.update({'links': 'links'})

    def test_list_to_api(self):
        expected_result = '{"items": [{"api_key_1": 1, "api_key_2": "2", "api_key_3": [1, "2"], "links": "links"}, {"api_key_1": 1, "api_key_2": "2", "api_key_3": [1, "2"], "links": "links"}], "total": 2}'

        list_model = [self.model, self.model]

        result = self.formatter.list_to_api(list_model)

        assert_that(result, equal_to(expected_result))

    @patch('xivo_restapi.helpers.mapper.map_to_api')
    def test_to_api(self, map_to_api):
        expected_result = '{"api_key_1": 1, "api_key_2": "2", "api_key_3": [1, "2"], "links": "links"}'

        map_to_api.return_value = self._api_data_dict

        result = self.formatter.to_api(self.model)

        assert_that(result, equal_to(expected_result))
        self._serializer.encode.assert_called_once_with(self._api_data_dict)
        map_to_api.assert_called_once_with(self._mapper.MAPPING, self._model_data_dict)
        self._mapper.add_links_to_dict.assert_called_once_with(self._api_data_dict, self.model)

    @patch('xivo_restapi.helpers.mapper.map_to_model')
    def test_to_model(self, map_to_model):
        expected_result = self.model
        api_data = '{"api_key_1": 1, "api_key_2": "2", "api_key_3": [1, "2"]}'

        map_to_model.return_value = self._model_data_dict

        result = self.formatter.to_model(api_data)

        assert_that(result, equal_to(expected_result))
        self._serializer.decode.assert_called_once_with(api_data)
        map_to_model.assert_called_once_with(self._mapper.MAPPING, self._api_data_dict)
        self._model_class.from_user_data.assert_called_once_with(self._model_data_dict)

    @patch('xivo_restapi.helpers.mapper.map_to_model')
    def test_to_model_update(self, map_to_model):
        my_model = Mock(model_key_1='lol',
                        model_key_2='lol',
                        model_key_3=['lol', 'lol'])

        def update_from_data(data_dict):
            for key, val in data_dict.iteritems():
                setattr(my_model, key, val)

        my_model.update_from_data.side_effect = update_from_data

        api_data = '{"api_key_1": 1, "api_key_2": "2", "api_key_3": [1, "2"]}'

        map_to_model.return_value = self._model_data_dict

        self.formatter.to_model_update(api_data, my_model)

        assert_that(my_model, all_of(
            has_property('model_key_1', self._model_data_dict['model_key_1']),
            has_property('model_key_2', self._model_data_dict['model_key_2']),
            has_property('model_key_3', self._model_data_dict['model_key_3'])
        ))
        map_to_model.assert_called_once_with(self._mapper.MAPPING, self._api_data_dict)
        my_model.update_from_data.assert_called_once_with(self._model_data_dict)
