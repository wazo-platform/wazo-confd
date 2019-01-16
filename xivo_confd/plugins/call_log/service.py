# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.call_log import dao as call_log_dao


class CallLogService(object):

    def __init__(self, dao):
        self.dao = dao

    def find_all(self):
        return self.dao.find_all()

    def find_all_in_period(self, start, end):
        self._validate_datetimes(start, end)
        return self.dao.find_all_in_period(start, end)

    def _validate_datetimes(self, start, end):
        missing_parameters = []
        if not start:
            missing_parameters.append('start_date')
        if not end:
            missing_parameters.append('end_date')

        if missing_parameters:
            raise errors.missing(*missing_parameters)


def build_service():
    return CallLogService(call_log_dao)
