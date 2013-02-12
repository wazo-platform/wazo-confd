# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
from xivo_dao.alchemy.recordings import Recordings
from xivo_restapi.rest.helpers import global_helper
import logging

logger = logging.getLogger()


def supplement_add_input(data):
    '''Returns the supplemented input'''
    logger.debug("Supplementing input for 'add_recording'")
    for key in data:
        if(data[key] == ''):
            data[key] = None
    return data


def create_instance(data):
    return global_helper.create_class_instance(Recordings, data)
