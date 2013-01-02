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
from xivo_dao import queue_features_dao
from xivo_dao.alchemy import dbconnection
from xivo_recording.dao.exceptions import DataRetrieveError, \
    NoSuchElementException
from xivo_recording.dao.generic_dao import GenericDao
from xivo_recording.dao.helpers.dynamic_formatting import \
    table_list_to_list_dict
from xivo_recording.recording_config import RecordingConfig
import datetime
import logging

logger = logging.getLogger(__name__)
logging.basicConfig()

class RecordCampaignDao(GenericDao):
    pass


class RecordCampaignDbBinder(object):

    __tablename__ = "record_campaign"

    def __init__(self, session):
        self.session = session
        
    def get_records_as_dict(self, search=None, checkCurrentlyRunning = False):

        tables = self.get_records(search, checkCurrentlyRunning)
        logger.debug("Tables retrieved:" + str(tables))
        table_dict = table_list_to_list_dict(tables)
        logger.debug("Tables dict:" + str(table_dict))
        return table_dict

    def get_records(self, search=None, checkCurrentlyRunning = False):
        my_query = self.session.query(RecordCampaignDao)
        if search != None:
            search_pattern = {}
            for item in search:
                if (item == 'queue_name'):
                    queue_features_dao.id_from_name(search["queue_name"])
                    search_pattern["queue_id"] = queue_features_dao.id_from_name(search["queue_name"])
                else:
                    search_pattern[item] = search[item]

            logger.debug("Search search_pattern: " + str(search_pattern))
            my_query = my_query.filter_by(**search_pattern)
        if checkCurrentlyRunning:
            now = datetime.datetime.now()
            my_query = my_query.filter(and_(RecordCampaignDao.start_date <= str(now), 
                                               RecordCampaignDao.end_date >= str(now)))
        return my_query.all()
        
    def id_from_name(self, name):
        result = self.session.query(RecordCampaignDao).filter_by(campaign_name = name).first()
        if result != None:
            return result.id
        else:
            raise DataRetrieveError("No campaign found for name " + name)

    def add(self, params):
        record = RecordCampaignDao()
        for k, v in params.items():
            setattr(record, k, v)
            #logger.debug("RecordCampaignDbBinder - add: " + str(k) + " = " + str(v))
        try:
            self.session.add(record)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.debug("RecordCampaignDbBinder - add: " + str(e))
            raise e
        return record.id
    
    def update(self, campaign_id, params):
        try:
            logger.debug('entering update')
            campaignsList = self.get_records({'id': campaign_id})
            logger.debug("Campaigns list for update: " + str(campaignsList))
            if(len(campaignsList) == 0):
                raise NoSuchElementException("No campaign found for id " + str(campaign_id))
            campaign = campaignsList[0]
            logger.debug('got original')
            for k, v in params.items():
                setattr(campaign, k, v)
                logger.debug("RecordCampaignDbBinder - update: " + k + " = " + v)
            logger.debug('attributes modified')
            self.session.add(campaign)
            self.session.commit()
            logger.debug('commited')
        except Exception as e:
            self.session.rollback()
            logger.debug('Impossible to update the campaign: ' + str(e))
            return False
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

