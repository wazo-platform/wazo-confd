# Copyright 2017-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import zoneinfo

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource


class TimezoneList(ConfdResource):
    @required_acl('confd.timezones.get')
    def get(self):
        timezones = sorted(zoneinfo.available_timezones())
        return {
            'total': len(timezones),
            'items': [{'zone_name': timezone} for timezone in timezones],
        }
