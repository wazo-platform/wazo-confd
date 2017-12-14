# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.iax_callnumberlimits import dao as iax_callnumberlimits_dao

from .notifier import build_notifier


class IAXCallNumberLimitsService(object):

    def __init__(self, dao, notifier):
        self.dao = dao
        self.notifier = notifier

    def list(self):
        return self.dao.find_all()

    def edit(self, resource):
        self.dao.edit_all(resource)
        self.notifier.edited(resource)


def build_service():
    return IAXCallNumberLimitsService(iax_callnumberlimits_dao,
                                      build_notifier())
