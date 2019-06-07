# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.asterisk_file import dao as asterisk_file_dao

from wazo_confd.helpers.asterisk import AsteriskConfigurationService

from .notifier import build_notifier


class HEPConfigurationService(AsteriskConfigurationService):

    file_name = 'hep.conf'


def build_service():
    return HEPConfigurationService(asterisk_file_dao,
                                   build_notifier())
