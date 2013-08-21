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

from xivo_restapi.helpers import mapper


class Formatter(object):

    def __init__(self, mapper, serializer, model_class):
        self._mapper = mapper
        self._serializer = serializer
        self._model_class = model_class

    def list_to_api(self, list_model):
        data_list = []
        for model in list_model:
            data_list.append(self._prepare_model_to_api(model))
        mapped_dict = self._process_paginated_data(data_list)
        api_data = self._serializer.encode(mapped_dict)
        return api_data

    def to_api(self, model):
        mapped_dict = self._prepare_model_to_api(model)
        api_data = self._serializer.encode(mapped_dict)
        return api_data

    def to_model(self, api_data):
        data_dict = self._serializer.decode(api_data)
        mapped_dict = mapper.map_to_model(self._mapper.MAPPING, data_dict)
        model_class = self._model_class.from_user_data(mapped_dict)
        return model_class

    def update_model(self, api_data, model_to_update):
        data_dict = self._serializer.decode(api_data)
        mapped_dict = mapper.map_to_model(self._mapper.MAPPING, data_dict)
        model_to_update.update_from_data(mapped_dict)

    def _prepare_model_to_api(self, model):
        model_dict = model.to_data_dict()
        mapped_dict = mapper.map_to_api(self._mapper.MAPPING, model_dict)
        self._mapper.add_links_to_dict(mapped_dict, model)
        return mapped_dict

    def _process_paginated_data(self, items):
        result = {
            'total': len(items),
            'items': items
        }
        return result
