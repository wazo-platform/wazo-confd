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
from xivo_recording.dao.exceptions import InvalidInputException
from xivo_recording.recording_config import RecordingConfig
import logging

logger = logging.getLogger(__name__)


def table_to_string(class_instance):
    members = vars(class_instance)
    result = ""
    for n in sorted(set(members)):
        if not n.startswith('_'):
            result += str(n) + ": " + str(getattr(class_instance, n)) + RecordingConfig.CSV_SEPARATOR
    return result.rstrip(",")


def table_list_to_list_dict(list_instance):
    list_of_dict = []

    for class_instance in list_instance:
        dict_instance = {}
        members = vars(class_instance)
        for elem in sorted(set(members)):
            if not elem.startswith('_'):
                value = getattr(class_instance, elem)
                #pour éviter d'avoir None au lieu de '' dans le résultat
                if value == None:
                    value = ''
                if type(value).__name__ != 'unicode':
                    value = str(value)
                dict_instance[elem] = value
        list_of_dict.append(dict_instance)
    return list_of_dict

def str_to_datetime(string):
    if(len(string) == 10):
        return datetime.strptime(string, "%Y-%m-%d")
    elif(len(string) == 19):
        return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    else:
        raise InvalidInputException("Invalid data provided", ["invalid_date_format"])