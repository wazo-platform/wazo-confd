# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import TimezoneList


class Plugin(object):

    def load(self, core):
        api = core['api']

        api.add_resource(
            TimezoneList,
            '/timezones'
        )
