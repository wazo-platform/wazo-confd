# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.features import dao as features_dao

from .notifier import build_notifier


class FeaturesConfigurationService(object):

    def __init__(self, dao, notifier):
        self.dao = dao
        self.notifier = notifier

    def list(self, section):
        return self.dao.find_all(section)

    def edit(self, section, variables):
        self.dao.edit_all(section, variables)
        self.notifier.edited(section, variables)


def build_service():
    return FeaturesConfigurationService(features_dao,
                                        build_notifier())
