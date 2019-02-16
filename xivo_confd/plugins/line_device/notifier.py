# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_confd import sysconfd


class LineDeviceNotifier(object):

    REQUEST_HANDLERS = {
        'ipbx': ['module reload chan_sccp.so'],
        'agentbus': [],
        'ctibus': [],
    }

    def __init__(self, sysconfd):
        self.sysconfd = sysconfd

    def associated(self, line, device):
        self._reload_sccp(line)

    def dissociated(self, line, device):
        self._reload_sccp(line)

    def _reload_sccp(self, line):
        if line.endpoint == "sccp":
            self.sysconfd.exec_request_handlers(self.REQUEST_HANDLERS)


def build_notifier():
    return LineDeviceNotifier(sysconfd)
