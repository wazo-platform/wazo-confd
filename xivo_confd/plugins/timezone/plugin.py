# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import TimezoneList


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']

        api.add_resource(
            TimezoneList,
            '/timezones'
        )
