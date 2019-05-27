# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.cti_profile import dao as cti_profile_dao
from xivo_dao.resources.utils.search import SearchResult


class CtiProfileService:

    def __init__(self, dao):
        self.dao = dao

    def search(self, args):
        items = self.dao.find_all()
        return SearchResult(items=items, total=len(items))

    def get(self, profile_id):
        return self.dao.get(profile_id)


def build_service():
    return CtiProfileService(cti_profile_dao)
