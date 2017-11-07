# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.plugins.sip_general.notifier import build_notifier

from xivo_dao.resources.sip_general import dao as sip_general_dao


class SIPGeneralService(object):

    def __init__(self, dao, notifier):
        self.dao = dao
        self.notifier = notifier

    def list(self):
        return self.dao.find_all()

    def edit(self, resource):
        self.dao.edit_all(resource)
        self.notifier.edited(resource)


def build_service():
    return SIPGeneralService(sip_general_dao,
                             build_notifier())
