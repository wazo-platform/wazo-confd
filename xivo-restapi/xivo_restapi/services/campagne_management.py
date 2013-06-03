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

from datetime import datetime
from xivo_dao import queue_dao, record_campaigns_dao
from xivo_dao.alchemy.record_campaigns import RecordCampaigns
from xivo_restapi.rest.helpers.global_helper import str_to_datetime
from xivo_restapi.restapi_config import RestAPIConfig
from xivo_restapi.services.utils.exceptions import DataRetrieveError, \
    NoSuchElementException, InvalidInputException
from xivo_restapi.services.utils.time_interval import TimeInterval
import logging

logger = logging.getLogger(__name__)
data_access_logger = logging.getLogger(RestAPIConfig.DATA_ACCESS_LOGGERNAME)


class CampagneManagement(object):

    def __init__(self):
        pass

    def create_campaign(self, campaign):
        data_access_logger.info("Creating a campaign with data %s."
                                % campaign.todict())
        self._validate_campaign(campaign)
        return record_campaigns_dao.add_or_update(campaign)

    def get_campaigns(self, search={}, checkCurrentlyRunning=False, paginator=None):
        search_pattern = {}
        for item in search:
            if item == 'queue_name':
                search_pattern["queue_id"] = queue_dao.id_from_name(search["queue_name"])
            else:
                search_pattern[item] = search[item]
        if paginator is None:
            paginator = (0, 0)
        (total, items) = record_campaigns_dao.get_records(search,
                                                          checkCurrentlyRunning,
                                                          paginator)
        try:
            for item in items:
                if item.queue_id is not None:
                    item.queue_name = queue_dao.queue_name(item.queue_id)
                    item.queue_display_name, item.queue_number = queue_dao.get_display_name_number(item.queue_id)

        except Exception as e:
            message = "DAO failure (%s)!" % e
            logger.critical(message)
            raise DataRetrieveError(message)

        return (total, items)

    def update_campaign(self, campaign_id, params):
        data_access_logger.info("Updating campaign of id %s with data %s."
                                % (campaign_id, params))
        logger.debug("Retrieving original campaign")
        campaign = record_campaigns_dao.get(campaign_id)
        if campaign is None:
            raise NoSuchElementException('No such campaign')
        logger.debug('Going to update')
        campaign = self._update_campaign_with_params(campaign, params)
        self._validate_campaign(campaign)
        result = record_campaigns_dao.add_or_update(campaign)
        return result

    def delete(self, campaign_id):
        data_access_logger.info("Deleting campaign of id %s.", campaign_id)
        campaign = record_campaigns_dao.get(int(campaign_id))
        if campaign is None:
            raise NoSuchElementException("No such campaign")
        else:
            record_campaigns_dao.delete(campaign)

    def _validate_campaign(self, campaign):
        '''Check if the campaign is valid, throws
        with a list of errors if it is not the case.'''
        errors_list = []
        logger.debug("validating campaign")
        if campaign.campaign_name is None:
            errors_list.append("empty_name")
        if campaign.start_date > campaign.end_date:
            errors_list.append("start_greater_than_end")
        else:
            criteria = {'queue_id': campaign.queue_id}
            paginator = (0, 0)
            (total, campaigns_list) = record_campaigns_dao.get_records(criteria,
                                                                       False,
                                                                       paginator)
            campaigns_list = [item for item in campaigns_list if item.id != campaign.id]
            intersects = self._check_for_interval_overlap(campaign, campaigns_list)
            if intersects:
                errors_list.append("concurrent_campaigns")
        if len(errors_list) > 0:
            raise InvalidInputException("Invalid data provided", errors_list)
        return campaign.id

    def _update_campaign_with_params(self, campaign, params):
        for k, v in params.items():
            if (k == 'start_date' or k == 'end_date') and not isinstance(v, datetime):
                v = str_to_datetime(v)
            if k in dir(RecordCampaigns):
                setattr(campaign, k, v)
        return campaign

    def _check_for_interval_overlap(self, campaign, campaigns_list):
        #check if another campaign exists on the same queue,
        #with a concurrent time interval:
        campaign_interval = TimeInterval(campaign.start_date, campaign.end_date)
        intersects = False
        for item in campaigns_list:
            item_interval = TimeInterval(item.start_date,
                                         item.end_date)
            if campaign_interval.intersect(item_interval) is not None:
                intersects = True
                break
        return intersects
