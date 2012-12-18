#!/usr/bin/python
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from gevent import httplib
from xivo.agi import AGI
from xivo_recording.recording_config import RecordingConfig
from xivo_recording.rest import rest_encoder
import logging
import sys
import traceback

DEBUG_MODE = True
LOGFILE = '/var/log/asterisk/xivo-recording-agi.log'

GENERIC_ERROR = 1
REST_ERROR = 2

agi = AGI()
logger = logging.getLogger()


class RestAPIError(Exception):
    pass


class Syslogger(object):

    def write(self, data):
        global logger
        logger.error(data)


def get_variables():
    xivo_vars = {}
    xivo_vars['queue_name'] = agi.get_variable('XIVO_QUEUENAME')
    xivo_vars['xivo-srcnum'] = agi.get_variable('XIVO_SRCNUM')
    xivo_vars['xivo-destnum'] = agi.get_variable('XIVO_DESTNUM')
    logger.debug("Queue_name = " + xivo_vars['queue_name'])
    return xivo_vars


def get_campaigns(queue_name):
    connection = httplib.HTTPConnection(
                            RecordingConfig.XIVO_RECORD_SERVICE_ADDRESS +
                            ":" +
                            str(RecordingConfig.XIVO_RECORD_SERVICE_PORT)
                        )

    requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                    RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/"
    param_str = "?activated=true&queue_name=%s" % str(queue_name)

    requestURI += param_str
    logger.debug("Getting campaigns from URL: " + requestURI)

    headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

    connection.request("GET", requestURI, None, headers)

    reply = connection.getresponse()

    if (reply.status != 200):
        logger.warning("Get campaigns failed with code: " + str(reply.status))
        raise RestAPIError()

    return reply.read()


def decodeCampaigns(campaign):
    if (len(campaign) == 0):
        return None
    campaigns = rest_encoder.decode(campaign)
    return campaigns


def init_logging(debug_mode):
    if debug_mode:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    logfilehandler = logging.FileHandler(LOGFILE)
    logger.addHandler(logfilehandler)

    syslogger = Syslogger()
    sys.stderr = syslogger


def determinateRecord():
    logger.debug("Going to determinate whether call is to be recorded")
    xivo_vars = get_variables()

    campaigns = None
    try:
        campaigns = decodeCampaigns(get_campaigns(xivo_vars['queue_name']))
    except RestAPIError:
        logger.error("REST WS: GET campaigns error")
        sys.exit(REST_ERROR)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)))
        sys.exit(GENERIC_ERROR)

    logger.debug("Campaigns: " + str(campaigns))
    base_filename = campaigns[0]['base_filename']

    if len(base_filename) == 0:
        logger.info("No base_filename")
        base_filename = campaigns[0]['campaign_name']

    logger.debug("Base filename: " + base_filename)
    if (campaigns[0]['activated'] == "True"):
        agi.set_variable('QR_RECORDQUEUE', '1')
        agi.set_variable('_QR_CAMPAIGN_NAME', campaigns[0]['campaign_name'])
        agi.set_variable('_QR_BASE_FILENAME', base_filename)
        logger.info('Calls to queue: "' +
                    xivo_vars['queue_name'] +
                    '" are recorded')
    else:
        agi.set_variable('QR_RECORDQUEUE', '0')
        logger.info('Calls to queue: "' +
                    xivo_vars['queue_name'] +
                    '" are not recorded')

    sys.exit(0)


def saveCallDetails():
    logger.debug("Save recorded call details")


def main():
    init_logging(DEBUG_MODE)
    try:
        if len(sys.argv) != 2:
            logger.error("wrong number of arguments")
            sys.exit(1)
        action = sys.argv[1]
        if (action == 'determinateRecord'):
            determinateRecord()
        elif (action == 'saveCallDetails'):
            saveCallDetails()
        else:
            logger.warning("No action given, exit")
            sys.exit(0)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)))


if __name__ == '__main__':
    main()
