# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import sysconfd


class LineDeviceNotifier(object):

    REQUEST_HANDLERS = {'ipbx': ['module reload chan_sccp.so'],
                        'agentbus': [],
                        'ctibus': []}

    def __init__(self, sysconfd):
        self.sysconfd = sysconfd

    def associated(self, line, device):
        self.reload_sccp(line)

    def dissociated(self, line, device):
        self.reload_sccp(line)

    def reload_sccp(self, line):
        if line.endpoint == "sccp":
            self.sysconfd.exec_request_handlers(self.REQUEST_HANDLERS)


def build_notifier():
    return LineDeviceNotifier(sysconfd)
