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

from sqlalchemy.exc import OperationalError
from xivo_dao.alchemy import dbconnection
from xivo_recording.recording_config import RecordingConfig
import logging

logger = logging.getLogger(__name__)


def _init_db_connection(binderClass=None):
    '''Initialise la connexion à la base de données, et renvoie, si nécessaire,
    une instance de la classe passée en paramètre. Cette classe doit posséder
    une méthode statique new_from_uri()'''
    dbconnection.unregister_db_connection_pool()
    dbconnection.register_db_connection_pool(
                     dbconnection.DBConnectionPool(dbconnection.DBConnection))
    dbconnection.add_connection(RecordingConfig.RECORDING_DB_URI)
    dbconnection.add_connection_as(RecordingConfig.RECORDING_DB_URI,
                                   'asterisk')
    if binderClass != None:
        return binderClass.new_from_uri(RecordingConfig.RECORDING_DB_URI)


def reconnectable(attribute_name):
    '''Décorateur permettant de rétablir la connexion à la base de données si
    elle a été perdue. Il est à utiliser sur les méthodes (uniquement les
    méthodes, pas les fonctions simples) faisant appel aux DAO.
    Il prend en paramètre le nom de l'attribut responsable de la connexion à
    la base de données (xxxDbBinder).
    Si un tel attribut n'existe pas, "None" doit être passé en paramètre.
    Une méthode utilisant ce décorateur doit "laisser passer" les exceptions
    de type OperationalError'''
    def reconnector(func):
        def reconnected_func(self, *args, **kwargs):
            global logger
            logger.debug("entering reconnected_func")
            try:
                result = func(self, *args, **kwargs)
            except OperationalError:
                logger.debug("got an error in reconnected_func")
                if(attribute_name == None):
                    _init_db_connection()
                else:
                    attr_value = _init_db_connection(
                                    getattr(self, attribute_name).__class__)
                    setattr(self, attribute_name, attr_value)
                result = func(self, *args, **kwargs)
            return result
        return reconnected_func
    return reconnector
