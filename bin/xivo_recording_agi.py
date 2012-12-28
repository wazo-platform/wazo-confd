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


def get_general_variables():
    xivo_vars = {}
    xivo_vars['queue_name'] = agi.get_variable('XIVO_QUEUENAME')
    xivo_vars['xivo_srcnum'] = agi.get_variable('XIVO_SRCNUM')
    xivo_vars['xivo_destnum'] = agi.get_variable('XIVO_DESTNUM')
    logger.debug(str(xivo_vars))
    return xivo_vars


def get_detailed_variables():
    xivo_vars = {}
    xivo_vars['campaign_id'] = agi.get_variable('QR_CAMPAIGN_ID')
    xivo_vars['base_filename'] = agi.get_variable('QR_BASE_FILENAME')
    xivo_vars['agent'] = agi.get_variable('QR_AGENT_NB')
    xivo_vars['callee'] = agi.get_variable('QR_CALLEE_NB')
    xivo_vars['caller'] = agi.get_variable('QR_CALLER_NB')
    xivo_vars['start_time'] = agi.get_variable('QR_TIME')
    xivo_vars['cid'] = agi.get_variable('UNIQUEID')
    xivo_vars['queue_name'] = agi.get_variable('QR_QUEUENAME')
    logger.debug(str(xivo_vars))
    return xivo_vars


def get_campaigns(queue_id):
    connection = RecordingConfig.getWSConnection()

    requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                    RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/"
    param_str = "?activated=true&queue_id=%s&running=true" % str(queue_id)

    requestURI += param_str
    logger.debug("Getting campaigns from URL: " + requestURI)

    headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

    connection.request("GET", requestURI, None, headers)

    reply = connection.getresponse()

    if (reply.status != 200):
        logger.warning("Get campaigns failed with code: " + str(reply.status))
        raise RestAPIError()

    return reply.read()


def init_logging(debug_mode):
    if debug_mode:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    logfilehandler = logging.FileHandler(LOGFILE)
    logger.addHandler(logfilehandler)

    syslogger = Syslogger()
    sys.stderr = syslogger


# TODO: Refactor in library, used here, in lettuce...!
def get_queues():
    connection = RecordingConfig.getWSConnection()

    requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                    RecordingConfig.XIVO_QUEUES_SERVICE_PATH + "/"

    logger.debug("Getting queues from URL: " + requestURI)

    headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

    connection.request("GET", requestURI, None, headers)

    reply = connection.getresponse()

    if (reply.status != 200):
        logger.warning("Get campaigns failed with code: " + str(reply.status))
        raise RestAPIError()

    return reply.read()


def get_queue_id(queue_name):
    queues = rest_encoder.decode(get_queues())
    for queue in queues:
        if queue['name'] == queue_name:
            return queue['id']

    return None


def determinate_record():
    logger.debug("Going to determinate whether call is to be recorded")
    xivo_vars = get_general_variables()

    queue_id = get_queue_id(xivo_vars['queue_name'])
    if queue_id == None:
        logger.error('Queue "' + xivo_vars['queue_name'] + '" not found!')
        sys.exit(1)
    campaigns = rest_encoder.decode(get_campaigns(queue_id))

    logger.debug("Campaigns: " + str(campaigns))
    base_filename = campaigns[0]['base_filename']

    if len(base_filename) == 0:
        logger.info("No base_filename")
        base_filename = campaigns[0]['campaign_name']

    logger.debug("Base filename: " + base_filename)
    if (campaigns[0]['activated'] == "True"):
        agi.set_variable('QR_RECORDQUEUE', '1')
        agi.set_variable('__QR_CAMPAIGN_ID', campaigns[0]['id'])
        agi.set_variable('__QR_BASE_FILENAME', base_filename)
        logger.info('Calls to queue: "' +
                    xivo_vars['queue_name'] +
                    '" are recorded')
    else:
        agi.set_variable('QR_RECORDQUEUE', '0')
        logger.info('Calls to queue: "' +
                    xivo_vars['queue_name'] +
                    '" are not recorded')

    sys.exit(0)


def save_recording(recording):
    connection = RecordingConfig.getWSConnection()

    requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                    RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                    recording['id'] + "/"

    logger.debug("Post recording to URL: " + requestURI)

    headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
    body = rest_encoder.encode(recording)
    logger.debug("Recording post body: " + str(body))
    connection.request("POST", requestURI, body, headers)

    reply = connection.getresponse()

    if (reply.status == 201):
        return 0
    else:
        logger.warning("POST recording failed with code: " + str(reply.status))
        raise RestAPIError()


def save_call_details():
    logger.debug("Save recorded call details")
    xivo_vars = get_detailed_variables()
    if xivo_vars['base_filename'] == "":
        xivo_vars['base_filename'] = 'NoBaseFilename'

    filename = xivo_vars['base_filename'] + xivo_vars['cid'] + '.wav'
    agi.set_variable('_QR_FILENAME', filename)
    recording = {}
    recording['cid'] = xivo_vars['cid']
    recording['filename'] = filename
    recording['id'] = xivo_vars['campaign_id']
    recording['start_time'] = xivo_vars['start_time']
    recording['agent'] = xivo_vars['agent']
    recording['caller'] = xivo_vars['caller']
    recording['callee'] = xivo_vars['callee']
    sys.exit(save_recording(recording))


def main():
    init_logging(DEBUG_MODE)
    try:
        if len(sys.argv) != 2:
            logger.error("wrong number of arguments")
            sys.exit(1)
        action = sys.argv[1]
        if (action == 'determinateRecord'):
            determinate_record()
        elif (action == 'saveCallDetails'):
            save_call_details()
        else:
            logger.warning("No action given, exit")
            sys.exit(0)
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)))


if __name__ == '__main__':
    main()
