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
from xivo_dao.alchemy.agentfeatures import AgentFeatures
from xivo_restapi.dao.generic_dao import GenericDao
from xivo_restapi.dao.helpers.query_utils import get_all_data, \
    get_paginated_data
from xivo_dao.helpers import config
import logging
from xivo_dao.helpers.db_manager import daosession_class

logger = logging.getLogger(__name__)
logging.basicConfig()


class RecordingDetailsDao(GenericDao):
    pass


class RecordingDetailsDbBinder(object):

    __tablename__ = "recording"

    def __init__(self):
        self._new_from_uri(config.DB_URI)

    @daosession_class
    def get_recordings_as_list(self, session, campaign_id, search=None, pagination=None):
        search_pattern = {}
        search_pattern['campaign_id'] = campaign_id
        if search != None:
            for item in search:
                    search_pattern[item] = search[item]

        logger.debug("Search search_pattern: " + str(search_pattern))
        my_query = session.query(RecordingDetailsDao)\
                                       .filter_by(**search_pattern)
        if (pagination == None):
            return get_all_data(session, my_query)
        else:
            return get_paginated_data(session, my_query, pagination)

    @daosession_class
    def add_recording(self, session, params):
        record = RecordingDetailsDao()
        for k, v in params.items():
            setattr(record, k, v)
        try:
            session.add(record)
            session.commit()
        except Exception as e:
            logger.error("SQL exception:" + e.message)
            session.rollback()
            raise e
        return True

    @daosession_class
    def search_recordings(self, session, campaign_id, key, pagination=None):
        logger.debug("campaign id = " + str(campaign_id)\
                      + ", key = " + str(key))
        #jointure interne:
        #RecordingDetailsDao r inner join AgentFeatures a on r.agent_id = a.id
        my_query = session.query(RecordingDetailsDao)\
                        .join((AgentFeatures, RecordingDetailsDao.agent_id == AgentFeatures.id))\
                        .filter(and_(RecordingDetailsDao.campaign_id == campaign_id, \
                                     or_(RecordingDetailsDao.caller == key,
                                         AgentFeatures.number == key)))
        if (pagination == None):
            return get_all_data(session, my_query)
        else:
            return get_paginated_data(session, my_query, pagination)

    @daosession_class
    def delete(self, session, campaign_id, recording_id):
        logger.debug("Going to delete " + str(recording_id))
        recording = session.query(RecordingDetailsDao)\
                    .filter(and_(RecordingDetailsDao.cid == recording_id,
                                 RecordingDetailsDao.campaign_id == campaign_id)) \
                    .first()

        if(recording == None):
            return None
        else:
            filename = recording.filename
            session.delete(recording)
            session.commit()
            return filename

    @daosession_class
    def count_recordings(self, session, campaign_id):
        return session.query(RecordingDetailsDao)\
            .filter(RecordingDetailsDao.campaign_id == campaign_id).count()

    def _new_from_uri(self, uri):
        try:
            class_mapper(RecordingDetailsDao)
        except UnmappedClassError:
            engine = create_engine(uri,
                                   encoding='utf-8')
            metadata = MetaData(engine)
            data = Table(self.__tablename__, metadata, autoload=True)
            mapper(RecordingDetailsDao, data)
