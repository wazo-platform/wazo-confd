# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.asterisk_file import dao as asterisk_file_dao

from .notifier import build_notifier


class ConfBridgeConfigurationService(object):

    file_name = 'confbridge.conf'

    def __init__(self, dao, notifier):
        self.dao = dao
        self.notifier = notifier

    def list(self, section):
        confbridge = self.dao.find_by(name=self.file_name)
        if not confbridge:
            return []

        section = confbridge.sections.get(section)
        if not section:
            return []

        return section.variables

    def edit(self, section_name, variables):
        confbridge = self.dao.find_by(name=self.file_name)
        section = confbridge.sections.get(section_name)
        self.dao.edit_section_variables(section, variables)
        self.notifier.edited(section_name, confbridge)


def build_service():
    return ConfBridgeConfigurationService(asterisk_file_dao,
                                          build_notifier())
