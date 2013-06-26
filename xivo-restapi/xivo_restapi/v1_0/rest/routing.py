# -*- coding: UTF-8 -*-
#
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

import logging

from flask import Blueprint
from xivo_restapi import config
from xivo_restapi.v1_0.rest.API_agents import APIAgents
from xivo_restapi.v1_0.rest.API_campaigns import APICampaigns
from xivo_restapi.v1_0.rest.API_queues import APIQueues
from xivo_restapi.v1_0.rest.API_recordings import APIRecordings
from xivo_restapi.v1_0.rest.API_users import APIUsers
from xivo_restapi.v1_0.rest.API_voicemails import APIVoicemails
from xivo_restapi.v1_0.restapi_config import RestAPIConfig

logger = logging.getLogger(__name__)

root = Blueprint("root_%s" % config.VERSION_1_0,
                 __name__,
                 url_prefix=RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                 RestAPIConfig.XIVO_RECORDING_SERVICE_PATH)

queues_service = Blueprint("queues_service",
                           __name__,
                           url_prefix=RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                           RestAPIConfig.XIVO_QUEUES_SERVICE_PATH)

agents_service = Blueprint("agents_service",
                           __name__,
                           url_prefix=RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                           RestAPIConfig.XIVO_AGENTS_SERVICE_PATH)

users_service = Blueprint("users_service",
                          __name__,
                          url_prefix=RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                          RestAPIConfig.XIVO_USERS_SERVICE_PATH)

voicemails_service = Blueprint("voicemails_service",
                               __name__,
                               url_prefix=RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                               RestAPIConfig.XIVO_VOICEMAIL_SERVICE_PATH)


def _root_routes():
    campaigns = APICampaigns()
    recordings = APIRecordings()
    root.add_url_rule("/",
                      "get",
                      campaigns.get,
                      methods=["GET"])
    root.add_url_rule("/<campaign_id>",
                      "get",
                      campaigns.get,
                      methods=["GET"])
    root.add_url_rule('/',
                      "add_campaign",
                      campaigns.add_campaign,
                      methods=['POST'])
    root.add_url_rule('/<campaign_id>',
                      "update",
                      getattr(APICampaigns(), "update"),
                      methods=['PUT'])

    root.add_url_rule("/<campaign_id>",
                      "delete_campaign",
                      campaigns.delete,
                      methods=['DELETE'])

    root.add_url_rule("/<campaign_id>/search",
                      "search_recording",
                      recordings.search,
                      methods=["GET"])

    root.add_url_rule("/<campaign_id>/",
                      "list_recordings",
                      recordings.list_recordings,
                      methods=["GET"])

    root.add_url_rule("/<campaign_id>/",
                      "add_recording",
                      recordings.add_recording,
                      methods=["POST"])

    root.add_url_rule("/<campaign_id>/<recording_id>",
                      "delete",
                      recordings.delete,
                      methods=["DELETE"])


def _queue_routes():
    queues = APIQueues()
    queues_service.add_url_rule("/",
                                "list_queues",
                                queues.list_queues,
                                methods=["GET"])


def _agent_routes():
    agents = APIAgents()
    agents_service.add_url_rule("/",
                                "list_agents",
                                agents.list_agents,
                                methods=["GET"])


def _user_routes():
    users = APIUsers()
    users_service.add_url_rule("/",
                               "list",
                               users.list,
                               methods=["GET"])

    users_service.add_url_rule("/<userid>",
                               "get",
                               users.get,
                               methods=["GET"])

    users_service.add_url_rule("/",
                               "create",
                               users.create,
                               methods=["POST"])

    users_service.add_url_rule("/<userid>",
                               "edit",
                               users.edit,
                               methods=["PUT"])

    users_service.add_url_rule("/<userid>",
                               "delete",
                               users.delete,
                               methods=["DELETE"])


def _voicemail_routes():
    voicemails = APIVoicemails()
    voicemails_service.add_url_rule("/",
                                    "list",
                                    voicemails.list,
                                    methods=["GET"])

    voicemails_service.add_url_rule("/<voicemailid>",
                                    "edit",
                                    voicemails.edit,
                                    methods=["PUT"])


def create_routes():
    _root_routes()
    _queue_routes()
    _agent_routes()
    _user_routes()
    _voicemail_routes()
