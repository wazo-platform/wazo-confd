# -*- coding: utf-8 -*-

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

from xivo_restapi.v1_0.service_data_model.sdm_exception import IncorrectParametersException


class BaseSdm(object):

    def todict(self):
        result = {}
        for key, value in self.__dict__.iteritems():
            result[key] = self._process_value(value)
        return result

    def validate(self, data):
        invalid_params = []
        for param in data:
            if not hasattr(self, param):
                invalid_params.append(param)
        if invalid_params:
            raise IncorrectParametersException(*invalid_params)

        return True

    def _process_value(self, value):
        if(isinstance(value, BaseSdm)):
            return value.todict()
        elif(isinstance(value, list)):
            result = []
            for item in value:
                result.append(self._process_value(item))
            return result
        else:
            return value
