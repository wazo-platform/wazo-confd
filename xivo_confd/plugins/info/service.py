# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.infos import dao as info_dao


class InfoService(object):

    def __init__(self, dao):
        self.dao = dao

    def get(self):
        return self.dao.get()


def build_service():
    return InfoService(info_dao)
