# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class HAService(object):

    def __init__(self, notifier, sysconfd):
        self.notifier = notifier
        self.sysconfd = sysconfd

    def get(self):
        return self.sysconfd.get_ha_config()

    def edit(self, form):
        self.notifier.edited(form)
