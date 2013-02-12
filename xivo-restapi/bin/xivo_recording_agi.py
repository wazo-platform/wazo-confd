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

from datetime import datetime
from xivo.agi import AGI
from xivo_restapi.rest import rest_encoder
from xivo_restapi.restapi_config import RestAPIConfig
import argparse
import httplib
import logging
import sys
import traceback
import unicodedata

DEBUG_MODE = False
LOGFILE = '/var/log/xivo-recording-agi.log'

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


def getWSConnection():
    return httplib.HTTPConnection(
                        RestAPIConfig.XIVO_RECORD_SERVICE_ADDRESS +
                        ":" +
                        str(RestAPIConfig.XIVO_RECORD_SERVICE_PORT)
                    )


def validate_filename_string(data):
    s_ascii = unicodedata.normalize('NFKD', unicode(data)).encode('ASCII', 'ignore')
    s_clean = ''.join(c for c in s_ascii if c.isalnum())
    return s_clean.replace(' ', '')


def get_general_variables():
    xivo_vars = {}
    xivo_vars['queue_name'] = agi.get_variable('XIVO_QUEUENAME')
    xivo_vars['xivo_srcnum'] = agi.get_variable('XIVO_SRCNUM')
    xivo_vars['xivo_dstnum'] = agi.get_variable('XIVO_DSTNUM')
    logger.debug(str(xivo_vars))
    return xivo_vars


def get_detailed_variables():
    xivo_vars = {}
    xivo_vars['campaign_id'] = agi.get_variable('QR_CAMPAIGN_ID')
    xivo_vars['agent_id'] = agi.get_variable('QR_AGENT_ID')
    xivo_vars['caller'] = agi.get_variable('QR_CALLER_NB')
    xivo_vars['start_time'] = agi.get_variable('QR_TIME')
    xivo_vars['cid'] = agi.get_variable('UNIQUEID')
    xivo_vars['queue_name'] = agi.get_variable('QR_QUEUENAME')
    xivo_vars['client_id'] = agi.get_variable(
                    RestAPIConfig.XIVO_DIALPLAN_RECORDING_USERDATA_VAR_NAME)
    logger.debug(str(xivo_vars))
    return xivo_vars


def get_campaigns(queue_id):
    connection = getWSConnection()

    requestURI = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                    RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + "/"
    param_str = "?activated=true&queue_id=%s&running=true" % str(queue_id)

    requestURI += param_str
    logger.debug("Getting campaigns from URL: " + requestURI)

    headers = RestAPIConfig.CTI_REST_DEFAULT_CONTENT_TYPE

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
    connection = getWSConnection()

    requestURI = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                    RestAPIConfig.XIVO_QUEUES_SERVICE_PATH + "/"

    logger.debug("Getting queues from URL: " + requestURI)

    headers = RestAPIConfig.CTI_REST_DEFAULT_CONTENT_TYPE

    connection.request("GET", requestURI, None, headers)

    reply = connection.getresponse()

    if (reply.status != 200):
        logger.warning("Get queues failed with code: " + str(reply.status))
        raise RestAPIError()

    return reply.read()


def get_queue_id(queue_name):
    queues = rest_encoder.decode(get_queues())
    for queue in queues:
        if queue['name'] == queue_name:
            return queue['id']

    return None


def get_agents():
    connection = getWSConnection()

    requestURI = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                    RestAPIConfig.XIVO_AGENTS_SERVICE_PATH + "/"

    logger.debug("Getting agents from URL: " + requestURI)

    headers = RestAPIConfig.CTI_REST_DEFAULT_CONTENT_TYPE

    connection.request("GET", requestURI, None, headers)

    reply = connection.getresponse()

    if (reply.status != 200):
        logger.warning("Get agents failed with code: " + str(reply.status))
        raise RestAPIError()

    return reply.read()


def get_agent_full_name(agent_id):
    try:
        agents = rest_encoder.decode(get_agents())
    except RestAPIError:
        logger.error('Unable to get campaigns via REST WS, using default filename.')
        return RestAPIConfig.RECORDING_FILENAME_WHEN_NO_AGENTNAME + \
                                                    str(agent_id)

    for agent in agents:
        if agent['id'] == int(agent_id):
            return validate_filename_string(agent['lastname']) + \
                    '_' + \
                    validate_filename_string(agent['firstname'])

    return RestAPIConfig.RECORDING_FILENAME_WHEN_NO_AGENTNAME + \
                                                    str(agent_id)


def set_user_field():
    agi.set_variable(
                 "__" + \
                 RestAPIConfig.XIVO_DIALPLAN_RECORDING_USERDATA_VAR_NAME,
                 agi.get_variable(RestAPIConfig.XIVO_DIALPLAN_CLIENTFIELD))


def determinate_record():
    logger.debug("Going to determinate whether call is to be recorded")
    xivo_vars = get_general_variables()

    try:
        queue_id = get_queue_id(xivo_vars['queue_name'])
    except RestAPIError:
        logger.error('Unable to get queues via REST WS, exiting.')
        sys.exit(1)

    if queue_id == None:
        agi.set_variable('QR_RECORDQUEUE', '0')
        logger.error('Queue "' + xivo_vars['queue_name'] + '" not found!')
        sys.exit(1)

    try:
        campaigns = rest_encoder.decode(get_campaigns(queue_id))['data']
    except RestAPIError:
        logger.error('Unable to get campaigns via REST WS, exiting.')
        sys.exit(1)

    logger.debug("Campaigns: " + str(campaigns))
    if(campaigns == []):
        agi.set_variable('QR_RECORDQUEUE', '0')
        logger.info('No activated campaign for queue: ' + \
                     xivo_vars['queue_name'])
        sys.exit(0)

    if (campaigns[0]['activated']):
        agi.set_variable('QR_RECORDQUEUE', '1')
        agi.set_variable('__QR_CAMPAIGN_ID', campaigns[0]['id'])
        set_user_field()
        logger.info('Calls to queue: "' +
                    xivo_vars['queue_name'] +
                    '" are recorded')
    else:
        agi.set_variable('QR_RECORDQUEUE', '0')
        logger.info('Calls to queue: "' +
                    xivo_vars['queue_name'] +
                    '" are not recorded')


def save_recording(recording):
    connection = getWSConnection()

    requestURI = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                    RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                    recording['campaign_id'] + "/"

    logger.debug("Post recording to URL: " + requestURI)

    headers = RestAPIConfig.CTI_REST_DEFAULT_CONTENT_TYPE
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

    filename = get_filename(xivo_vars['agent_id'],
                            xivo_vars['cid'])
    agi.set_variable('_QR_FILENAME', filename)
    recording = {}
    recording['cid'] = xivo_vars['cid']
    recording['filename'] = filename
    recording['campaign_id'] = xivo_vars['campaign_id']
    recording['start_time'] = xivo_vars['start_time']
    recording['agent_id'] = xivo_vars['agent_id']
    recording['caller'] = xivo_vars['caller']
    recording['client_id'] = xivo_vars['client_id']
    sys.exit(save_recording(recording))


def get_filename(agent_id, call_id):
    return get_agent_full_name(agent_id) + \
                '_' + \
                str(call_id) + \
                '.wav'


def process_call_hangup(cid, campaign_id):
    connection = getWSConnection()
    requestURI = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                    RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + "/" + \
                    campaign_id + "/" + cid
    body = {"end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    logger.debug("Update recording to URL: " + requestURI)
    headers = RestAPIConfig.CTI_REST_DEFAULT_CONTENT_TYPE
    connection.request("PUT", requestURI, rest_encoder.encode(body), headers)

    reply = connection.getresponse()

    if (reply.status == 200):
        sys.exit(0)
    else:
        logger.warning("PUT recording failed with code: " + str(reply.status))
        raise RestAPIError()


def process_call_hangup_args():
    parser = _new_parser()
    if(len(sys.argv) < 6):
        logger.error('processCallHangup must be called with parameters ' + \
                     'time, cid and campaign')
        sys.exit(1)
    parsing_res = parser.parse_args(sys.argv[2:])
    process_call_hangup(parsing_res.cid, parsing_res.campaign)


def _new_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cid')
    parser.add_argument('--campaign')
    return parser


def main():
    init_logging(DEBUG_MODE)
    try:
        if len(sys.argv) < 2:
            logger.error("wrong number of arguments")
            sys.exit(1)
        option_dict = {
                       'determinateRecord': determinate_record,
                       'saveCallDetails': save_call_details,
                       'processCallHangup': process_call_hangup_args}
        if(sys.argv[1] not in option_dict):
            logger.error("Invalid argument provided: " + sys.argv[1])
            sys.exit(1)
        option_dict[sys.argv[1]]()
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback)))
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
