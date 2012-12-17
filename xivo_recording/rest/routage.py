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
from xivo_recording.recording_config import RecordingConfig
from xivo_recording.rest.API_recordings import APIRecordings
from xivo_recording.rest.API_campaigns import APICampaigns

logger = logging.getLogger(__name__)

root = Blueprint("root",
                 __name__,
                 url_prefix=RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH +
                            RecordingConfig.XIVO_RECORDING_SERVICE_PATH)

# ****************** #
#   API campaigns    #
# ****************** #

root.add_url_rule("/",
                  "list_campaigns",
                  getattr(APICampaigns(), "list_campaigns"),
                  methods=["GET"])

root.add_url_rule("/<campaign_name>",
                  "get",
                  getattr(APICampaigns(), "get"),
                  methods=["GET"])

root.add_url_rule('/',
                  'add_campaign',
                  getattr(APICampaigns(), "add_campaign"),
                  methods=['POST'])

root.add_url_rule('/<campaign_name>',
                  'update',
                  getattr(APICampaigns(), "update"),
                  methods=['PUT'])

root.add_url_rule('/<campaign_name>',
                  'delete',
                  getattr(APICampaigns(), "delete"),
                  methods=['DELETE'])


# ****************** #
#   API recordings   #
# ****************** #

root.add_url_rule("/<campaign_name>/",
                  "list_recordings",
                  getattr(APIRecordings(), "list_recordings"),
                  methods=["GET"])

root.add_url_rule("/<campaign_name>/",
                  "add_recording",
                  getattr(APIRecordings(), "add_recording"),
                  methods=["POST"])
