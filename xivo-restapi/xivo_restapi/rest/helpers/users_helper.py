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

from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_restapi.rest.helpers import global_helper
from xivo_dao.service_data_model.sdm_exception import IncorrectParametersException


class UsersHelper:

    def __init__(self):
        self.accepted_fields = [column.name for column in\
                                 UserFeatures.__table__.columns] #@UndefinedVariable

    def create_instance(self, data):
        self.validate_data(data)
        return global_helper.create_class_instance(UserFeatures, data)

    def validate_data(self, data):
        invalid_params = []
        for param in data:
            if(param not in self.accepted_fields):
                invalid_params.append(param)
        if(len(invalid_params) > 0):
            raise IncorrectParametersException(*invalid_params)
