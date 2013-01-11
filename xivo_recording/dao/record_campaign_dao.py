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

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.schema import Table, MetaData
from sqlalchemy.sql.expression import and_
from xivo_dao.alchemy import dbconnection
from xivo_recording.dao.exceptions import DataRetrieveError, \
    NoSuchElementException, InvalidInputException
from xivo_recording.dao.generic_dao import GenericDao
from xivo_recording.dao.helpers.dynamic_formatting import \
    table_list_to_list_dict, str_to_datetime
from xivo_recording.recording_config import RecordingConfig
from datetime import datetime
import logging
from xivo_recording.dao.helpers.query_utils import get_all_data,\
    get_paginated_data

logger = logging.getLogger(__name__)
logging.basicConfig()


class RecordCampaignDao(GenericDao):
    pass


class RecordCampaignDbBinder(object):

    __tablename__ = "record_campaign"

    def __init__(self, session):
        self.session = session

    def get_records(self, search=None, checkCurrentlyRunning=False, pagination=None):
        my_query = self.session.query(RecordCampaignDao)
        if search != None:
            logger.debug("Search search_pattern: " + str(search))
            my_query = my_query.filter_by(**search)

        if checkCurrentlyRunning:
            now = datetime.now()
            my_query = my_query.filter(and_(RecordCampaignDao.start_date <= str(now),
                                               RecordCampaignDao.end_date >= str(now)))

        if (pagination == None):
            return get_all_data(self.session, my_query)
        else:
            return get_paginated_data(self.session, my_query, pagination)

    def id_from_name(self, name):
        result = self.session.query(RecordCampaignDao).filter_by(campaign_name=name).first()
        if result != None:
            return result.id
        else:
            raise DataRetrieveError("No campaign found for name " + name)

    def add(self, params):
        record = RecordCampaignDao()
        for k, v in params.items():
            if((k == "start_date" or k == "end_date") and type(v) == str):
                v = str_to_datetime(v)
            setattr(record, k, v)
        self._validate_campaign(record)
        try:
            logger.debug("inserting")
            self.session.add(record)
            logger.debug("commiting")
            self.session.commit()
        except Exception as e:
            try:
                self.session.rollback()
            except e:
                logger.error("Rollback failed with exception " + str(e))
            logger.error("RecordCampaignDbBinder - add: " + str(e))
            raise e
        logger.debug("returning")
        return record.id

    def update(self, campaign_id, params):
        try:
            logger.debug('entering update')
            campaignsList = self.session.query(RecordCampaignDao)\
                        .filter(RecordCampaignDao.id == campaign_id).all()
            logger.debug("Campaigns list for update: " + str(campaignsList))
            if(len(campaignsList) == 0):
                raise NoSuchElementException("No campaign found for id " + str(campaign_id))
            campaign = campaignsList[0]
            logger.debug('got original')
            for k, v in params.items():
                if(k == "start_date" or k == "end_date"):
                    v = str_to_datetime(v)
                setattr(campaign, k, v)
            logger.debug('attributes modified')
            self._validate_campaign(campaign)
            self.session.add(campaign)
            self.session.commit()
            logger.debug('commited')
        except Exception as e:
            self.session.rollback()
            logger.debug('Impossible to update the campaign: ' + str(e))
            raise e
        return True

    @classmethod
    def create_class_mapper(cls, uri):
        engine = create_engine(uri, echo=RecordingConfig.POSTGRES_DEBUG, encoding='utf-8')
        if (RecordingConfig.POSTGRES_DEBUG):
            loggerDB = logging.getLogger('sqlalchemy.engine')
            logfilehandler = logging.FileHandler(RecordingConfig.POSTGRES_DEBUG_FILE)
            loggerDB.addHandler(logfilehandler)
            loggerDB.setLevel(logging.DEBUG)

        metadata = MetaData(engine)
        data = Table(cls.__tablename__, metadata, autoload=True)
        mapper(RecordCampaignDao, data)

    @classmethod
    def new_from_uri(cls, uri):
        try:
            class_mapper(RecordCampaignDao)
        except UnmappedClassError:
            try:
                cls.create_class_mapper(uri)
            except BaseException as e:
                logger.error("Database access error: " + str(e.args))
                return None
        except BaseException as e:
            logger.error("Database access error:" + str(e.args))
            return None
        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())

    def _validate_campaign(self, record):
        '''Check if the campaign is valid, throws InvalidInputException
        with a list of errors if it is not the case.'''
        errors_list = []
        logger.debug("validating")
        if(record.campaign_name == None):
            errors_list.append("empty_name")
        if(record.start_date > record.end_date):
            errors_list.append("start_greater_than_end")

        if(len(errors_list) > 0):
            raise InvalidInputException("Invalid data provided", errors_list)
