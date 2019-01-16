# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

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
