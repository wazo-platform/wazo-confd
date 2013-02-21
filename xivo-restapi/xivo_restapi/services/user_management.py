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

from xivo_dao import user_dao
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_restapi.services.utils.exceptions import NoSuchElementException
import logging

logger = logging.getLogger(__name__)


class UserManagement:

    def __init__(self):
        self._user_columns = [column.name for column\
                               in UserFeatures.__table__.columns] #@UndefinedVariable

    def get_all_users(self):
        return user_dao.get_all()

    def get_user(self, userid):
        try:
            return user_dao.get(userid)
        except LookupError:
            raise NoSuchElementException("No such user")

    def create_user(self, user):
        if(user.description is None):
            user.description = ''
        user_dao.add_user(user)

    def edit_user(self, userid, data):
        final_data = self._clean_data_dict(data)
        updated_rows = user_dao.update(userid, final_data)
        if(updated_rows == 0):
            raise NoSuchElementException("No such user")

    def _clean_data_dict(self, data):
        bad_keys_list = [key for key in data if key == 'id' or key not in self._user_columns]
        for key in bad_keys_list:
            del data[key]
        return data

    def delete_user(self, userid):
        result = user_dao.delete(userid)
        if(result == 0):
            raise NoSuchElementException("No such user")
