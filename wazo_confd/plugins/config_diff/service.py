# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from wazo_confd._sysconfd import SysconfdPublisher

logger = logging.getLogger(__name__)


class ConfigHistoryService:
    def __init__(self, sysconfd):
        self.sysconfd: SysconfdPublisher = sysconfd

    def get_history(self):
        return self.sysconfd.get_config_history()

    def get_diff(self, start_date: str, end_date: str):
        return self.sysconfd.get_config_history_diff(start_date, end_date)
