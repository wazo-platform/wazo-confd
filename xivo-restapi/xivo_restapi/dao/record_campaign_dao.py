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

from datetime import datetime
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.schema import Table, MetaData
from sqlalchemy.sql.expression import and_
from xivo_restapi.dao.exceptions import DataRetrieveError, \
    NoSuchElementException, InvalidInputException
from xivo_restapi.dao.generic_dao import GenericDao
from xivo_restapi.dao.helpers.dynamic_formatting import str_to_datetime
from xivo_restapi.dao.helpers.query_utils import get_all_data, \
    get_paginated_data
from xivo_restapi.dao.helpers.time_interval import TimeInterval
from xivo_dao.helpers import config
import logging
from sqlalchemy.orm.util import class_mapper
from xivo_dao.helpers.db_manager import daosession_class

logger = logging.getLogger(__name__)
logging.basicConfig()


class RecordCampaignDao(GenericDao):
    pass


class RecordCampaignDbBinder(object):

    __tablename__ = "record_campaign"

    def __init__(self):
        self._new_from_uri(config.DB_URI)

    @daosession_class
    def get_records(self, session, search=None, checkCurrentlyRunning=False, pagination=None):
        my_query = session.query(RecordCampaignDao)
        if search != None:
            logger.debug("Search search_pattern: " + str(search))
            my_query = my_query.filter_by(**search)

        if checkCurrentlyRunning:
            now = datetime.now()
            my_query = my_query.filter(
                               and_(RecordCampaignDao.start_date <= str(now),
                                    RecordCampaignDao.end_date >= str(now)))

        if (pagination == None):
            return get_all_data(session, my_query)
        else:
            return get_paginated_data(session, my_query, pagination)

    @daosession_class
    def id_from_name(self, session, name):
        result = session.query(RecordCampaignDao)\
                    .filter_by(campaign_name=name)\
                    .first()
        if result != None:
            return result.id
        else:
            raise DataRetrieveError("No campaign found for name " + name)

    @daosession_class
    def add(self, session, params):
        record = RecordCampaignDao()
        for k, v in params.items():
            if((k == "start_date" or k == "end_date") and type(v) != datetime):
                v = str_to_datetime(v)
            setattr(record, k, v)
        self._validate_campaign(record)
        try:
            session.add(record)
            session.commit()
        except Exception as e:
            try:
                session.rollback()
            except e:
                logger.error("Rollback failed with exception " + str(e))
            logger.error("RecordCampaignDbBinder - add: " + str(e))
            raise e
        logger.debug("returning")
        return record.id

    @daosession_class
    def update(self, session, campaign_id, params):
        try:
            logger.debug('entering update')
            campaignsList = session.query(RecordCampaignDao)\
                        .filter(RecordCampaignDao.id == campaign_id).all()
            logger.debug("Campaigns list for update: " + str(campaignsList))
            if(len(campaignsList) == 0):
                raise NoSuchElementException("No campaign found for id " + \
                                             str(campaign_id))
            campaign = campaignsList[0]
            logger.debug('got original')
            for k, v in params.items():
                if((k == "start_date" or k == "end_date")
                                        and type(v) != datetime):
                    v = str_to_datetime(v)
                setattr(campaign, k, v)
            logger.debug('attributes modified')
            self._validate_campaign(campaign)
            session.add(campaign)
            session.commit()
            logger.debug('commited')
        except Exception as e:
            session.rollback()
            logger.debug('Impossible to update the campaign: ' + str(e))
            raise e
        return True

    def _new_from_uri(self, uri):
        try:
            class_mapper(RecordCampaignDao)
        except UnmappedClassError:
            engine = create_engine(uri,
                                   encoding='utf-8')
            metadata = MetaData(engine)
            data = Table(self.__tablename__, metadata, autoload=True)
            mapper(RecordCampaignDao, data)

    @daosession_class
    def _validate_campaign(self, session, record):
        '''Check if the campaign is valid, throws InvalidInputException
        with a list of errors if it is not the case.'''
        errors_list = []
        logger.debug("validating campaign")
        if(record.campaign_name == None):
            errors_list.append("empty_name")

        if(record.start_date > record.end_date):
            errors_list.append("start_greater_than_end")
        else:
            #check if another campaign exists on the same queue,
            #with a concurrent time interval:
            campaigns_list = session.query(RecordCampaignDao)\
                .filter(RecordCampaignDao.queue_id == record.queue_id)\
                .filter(RecordCampaignDao.id != record.id).all()
            record_interval = TimeInterval(record.start_date, record.end_date)
            intersects = False
            for campaign in campaigns_list:
                campaign_interval = TimeInterval(campaign.start_date,
                                                 campaign.end_date)
                if(record_interval.intersect(campaign_interval) != None):
                    intersects = True
                    break
            if(intersects):
                errors_list.append("concurrent_campaigns")

        if(len(errors_list) > 0):
            raise InvalidInputException("Invalid data provided", errors_list)

    @daosession_class
    def get(self, session, campaign_id):
        return session.query(RecordCampaignDao)\
            .filter(RecordCampaignDao.id == campaign_id).first()

    @daosession_class
    def delete(self, session, campaign):
        try:
            session.delete(campaign)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
