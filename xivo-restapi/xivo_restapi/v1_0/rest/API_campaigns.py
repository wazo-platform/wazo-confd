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

import logging

from flask import request
from flask.helpers import make_response
from sqlalchemy.exc import IntegrityError
from xivo_restapi.v1_0 import rest_encoder
from xivo_restapi.authentication.xivo_realm_digest import realmDigest
from xivo_restapi.v1_0.rest.helpers import global_helper
from xivo_restapi.v1_0.rest.helpers.campaigns_helper import CampaignsHelper
from xivo_restapi.v1_0.rest.helpers.global_helper import exception_catcher
from xivo_restapi.negotiate.flask_negotiate import consumes, produces
from xivo_restapi.v1_0.services.campagne_management import CampagneManagement
from xivo_restapi.v1_0.services.utils.exceptions import InvalidInputException


logger = logging.getLogger(__name__)


class APICampaigns(object):

    def __init__(self):
        self._campagne_manager = CampagneManagement()
        self._campaigns_helper = CampaignsHelper()

    @exception_catcher
    @consumes('application/json')
    @produces('application/json')
    @realmDigest.requires_auth
    def add_campaign(self):
        data = request.data.decode("utf-8")
        logger.debug("Got an ADD request for campaigns")
        body = rest_encoder.decode(data)
        logger.debug(str(body))
        body = self._campaigns_helper.supplement_add_input(body)
        campaign = self._campaigns_helper.create_instance(body)
        logger.debug("Just supplemented: %s", body)
        try:
            result = self._campagne_manager.create_campaign(campaign)
            logger.debug("Just created")
        except IntegrityError:
            body = ["duplicated_name"]
            return make_response(rest_encoder.encode(body), 400)
        except InvalidInputException as e:
            body = e.errors_list
            return make_response(rest_encoder.encode(body), 400)
        if (type(result) == int and result > 0):
            return make_response(rest_encoder.encode(result), 201)
        else:
            return make_response(rest_encoder.encode([str(result)]), 500)

    @exception_catcher
    @produces('application/json')
    @realmDigest.requires_auth
    def get(self, campaign_id=None):
        logger.debug("Got a GET request for campaign id: %s with args %s",
                     campaign_id, campaign_id)
        checkCurrentlyRunning = False
        params = {}
        if campaign_id is not None:
            params['id'] = campaign_id
        for item in request.args:
            if item == 'running':
                checkCurrentlyRunning = (request.args[item] == 'true')
            elif not item.startswith('_'):
                params[item] = request.args[item]
        paginator = global_helper.create_paginator(request.args)
        result = self._campagne_manager.get_campaigns(params,
                                                      checkCurrentlyRunning,
                                                      paginator)
        logger.debug("got result: %s", result)
        body = rest_encoder.encode(result)
        logger.debug("result encoded")
        return make_response(body, 200)

    @exception_catcher
    @produces('application/json')
    @realmDigest.requires_auth
    def delete(self, campaign_id):
        try:
            logger.debug("Got an DELETE request for campaign id: %s", campaign_id)
            self._campagne_manager.delete(campaign_id)
        except IntegrityError:
            liste = ["campaign_not_empty"]
            return make_response(rest_encoder.encode(liste), 412)
        return make_response(rest_encoder.encode("Deleted: True"), 200)

    @exception_catcher
    @consumes('application/json')
    @produces('application/json')
    @realmDigest.requires_auth
    def update(self, campaign_id):
        data = request.data.decode("utf-8")
        logger.debug("Got an UPDATE request for campaign id: %s", campaign_id)
        body = rest_encoder.decode(data)
        logger.debug(str(body))
        try:
            body = self._campaigns_helper.supplement_edit_input(body)
            result = self._campagne_manager.update_campaign(campaign_id, body)
        except IntegrityError:
            liste = ["duplicated_name"]
            return make_response(rest_encoder.encode(liste), 400)
        except InvalidInputException as e:
            liste = e.errors_list
            return make_response(rest_encoder.encode(liste), 400)
        if (result):
            body = rest_encoder.encode(("Updated: %s" % result))
            return make_response(body, 200)
        else:
            body = rest_encoder.encode([str(result)])
            return make_response(body, 500)
