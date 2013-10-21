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

import logging
import sys
import traceback

from datetime import datetime
from flask.helpers import make_response
from werkzeug.exceptions import HTTPException
from xivo_restapi.v1_0.services.utils.exceptions import InvalidInputException, \
    NoSuchElementException
from xivo_restapi.v1_0 import rest_encoder

logger = logging.getLogger(__name__)


def create_class_instance(class_type, data):
    instance = class_type()
    for k, v in data.items():
        logger.debug("Key: %s, value: %s", k, v)
        logger.debug("dir value: %s", dir)
        if k in instance.todict():
            setattr(instance, k, v)
    return instance


def create_paginator(data):
    if '_page' not in data or '_pagesize' not in data:
        return (0, 0)
    else:
        page = int(data['_page'])
        pagesize = int(data['_pagesize'])
        return (page, pagesize)


def str_to_datetime(string):
    if type(string) != str and type(string) != unicode:
        raise InvalidInputException("Invalid data provided",
                                    ["invalid_date_format"])
    if len(string) != 10 and len(string) != 19:
        raise InvalidInputException("Invalid data provided",
                                    ["invalid_date_format"])
    try:
        if len(string) == 10:
            result = datetime.strptime(string, "%Y-%m-%d")
            return result
        elif len(string) == 19:
            return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.error(repr(traceback.format_exception(exc_type, exc_value,
                     exc_traceback)))
        raise InvalidInputException("Invalid data provided",
                                    ["invalid_date_format"])


def exception_catcher(func):
    def decorated_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.exception(e)
            data = rest_encoder.encode(["No parsable data in the request"])
            return make_response(data, 400)
        except NoSuchElementException:
            return make_response('', 404)
        except HTTPException:
            raise
        except Exception as e:
            return make_response(rest_encoder.encode([str(e)]), 500)
    return decorated_func
