# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import pytz

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource


class TimezoneList(ConfdResource):

    @required_acl('confd.timezones.get')
    def get(self):
        timezones = pytz.all_timezones
        return {'total': len(timezones),
                'items': [{'zone_name': timezone} for timezone in timezones]}
