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

from xivo_confd.plugins.user.validator import build_validator
from xivo_confd.plugins.user.notifier import build_notifier

from xivo_confd.helpers.resource import CRUDService

from xivo_dao.resources.user import dao as user_dao


class UserService(CRUDService):

    def legacy_search(self, term):
        return self.dao.legacy_search(term)


def build_service():
    return UserService(user_dao,
                       build_validator(),
                       build_notifier())
