# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.infos import dao as info_dao


class InfoService:
    def __init__(self, dao):
        self.dao = dao

    def get(self):
        return self.dao.get()


def build_service():
    return InfoService(info_dao)
