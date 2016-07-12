# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_dao.resources.cti_profile import dao as cti_profile_dao
from xivo_dao.resources.utils.search import SearchResult


class CtiProfileService(object):

    def __init__(self, dao):
        self.dao = dao

    def search(self, args):
        items = self.dao.find_all()
        return SearchResult(items=items, total=len(items))

    def get(self, profile_id):
        return self.dao.get(profile_id)


def build_service():
    return CtiProfileService(cti_profile_dao)
