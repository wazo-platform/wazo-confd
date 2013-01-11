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
from sqlalchemy.sql.expression import or_, and_
from xivo_dao.alchemy import dbconnection
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_recording.dao.generic_dao import GenericDao
from xivo_recording.dao.helpers.dynamic_formatting import \
    table_list_to_list_dict
from xivo_recording.recording_config import RecordingConfig
import logging

logger = logging.getLogger(__name__)
logging.basicConfig()


class RecordingDetailsDao(GenericDao):
    pass


class RecordingDetailsDbBinder(object):

    __tablename__ = "recording"

    def __init__(self, session):
        self.session = session

    def get_recordings_as_list(self, campaign_id, search=None):
        search_pattern = {}
        search_pattern['campaign_id'] = campaign_id
        if search != None:
            for item in search:
                    search_pattern[item] = search[item]

        logger.debug("Search search_pattern: " + str(search_pattern))
        return table_list_to_list_dict(self.session.query(RecordingDetailsDao)\
                                       .filter_by(**search_pattern))

    def add_recording(self, params):
        record = RecordingDetailsDao()
        for k, v in params.items():
            setattr(record, k, v)
        try:
            self.session.add(record)
            self.session.commit()
        except Exception as e:
            logger.error("SQL exception:" + e.message)
            self.session.rollback()
            raise e
        return True

    def search_recordings(self, campaign_id, key):
        logger.debug("campaign id = " + str(campaign_id)\
                      + ", key = " + str(key))
        #jointure interne:
        #RecordingDetailsDao r inner join AgentFeatures a on r.agent_id = a.id
        query = self.session.query(RecordingDetailsDao)\
                        .join((AgentFeatures, RecordingDetailsDao.agent_id == AgentFeatures.id))\
                        .filter(and_(RecordingDetailsDao.campaign_id == campaign_id,\
                                     or_(RecordingDetailsDao.caller == key, AgentFeatures.number == key)))
        logger.debug("generated query: " + str(query))
        result = table_list_to_list_dict(query)
        logger.debug("Search result: " + str(result))
        return result

    def delete(self, campaign_id, recording_id):
        logger.debug("Going to delete " + str(recording_id))
        recording = self.session.query(RecordingDetailsDao)\
                    .filter(and_(RecordingDetailsDao.cid == recording_id, RecordingDetailsDao.campaign_id == campaign_id))\
                    .first()
        if(recording == None):
            return None
        else:
            filename = recording.filename
            self.session.delete(recording)
            self.session.commit()
            return filename

    @classmethod
    def new_from_uri(cls, uri):
        try:
            class_mapper(RecordingDetailsDao)
        except UnmappedClassError:
            engine = create_engine(uri, echo=RecordingConfig.POSTGRES_DEBUG, encoding='utf-8')
            metadata = MetaData(engine)
            data = Table(cls.__tablename__, metadata, autoload=True)
            mapper(RecordingDetailsDao, data)
        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())
