# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.asterisk_file import dao as asterisk_file_dao

from wazo_confd.helpers.asterisk import AsteriskConfigurationService

from .notifier import build_notifier


class PJSIPConfigurationService(AsteriskConfigurationService):

    file_name = 'pjsip.conf'

    def __init__(self, asterisk_file_dao, notifier, pjsip_doc):
        super().__init__(asterisk_file_dao, notifier)
        self.pjsip_doc = pjsip_doc


def build_service(pjsip_doc):
    return PJSIPConfigurationService(asterisk_file_dao, build_notifier(), pjsip_doc)
