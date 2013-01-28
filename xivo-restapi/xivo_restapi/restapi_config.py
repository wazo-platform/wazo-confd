# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

import httplib


class RestAPIConfig(object):

    XIVO_RECORD_SERVICE_ADDRESS = "127.0.0.1"
    XIVO_RECORD_SERVICE_PORT = 50050
    XIVO_REST_SERVICE_ROOT_PATH = "/rest"
    XIVO_RECORDING_SERVICE_PATH = "/IPBX/recording_campaigns"
    XIVO_QUEUES_SERVICE_PATH = "/CallCenter/queues"

    XIVO_DIALPLAN_RECORDING_USERDATA_VAR_NAME = 'RECORDING_USERFIELD'
    XIVO_DIALPLAN_CLIENTFIELD = 'LDLC_IDTICKET'
    CTI_REST_DEFAULT_CONTENT_TYPE = {"Content-Type:": "application/json"}

    CSV_SEPARATOR = ","

    POSTGRES_ADDRESS = "127.0.0.1"
    RECORDING_DB_URI = "postgresql://asterisk:proformatique@" + POSTGRES_ADDRESS + "/asterisk"

    RECORDING_FILE_ROOT_PATH = "/var/lib/pf-xivo/sounds/campagnes"

    POSTGRES_DEBUG = False
    POSTGRES_DEBUG_FILE = "/tmp/xivo-recording-postgres.log"

    def __init__(self):
        pass

    @classmethod
    def getWSConnection(cls):
        return httplib.HTTPConnection(
                            RestAPIConfig.XIVO_RECORD_SERVICE_ADDRESS +
                            ":" +
                            str(RestAPIConfig.XIVO_RECORD_SERVICE_PORT)
                        )
