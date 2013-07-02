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

from flask.helpers import make_response
from xivo_restapi.helpers import serializer
from werkzeug.exceptions import HTTPException
from xivo_dao.data_handler.exception import MissingParametersError, \
    InvalidParametersError, ElementAlreadyExistsError, ElementNotExistsError

logger = logging.getLogger(__name__)


def exception_catcher(func):
    def decorated_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MissingParametersError as e:
            data = serializer.encode([str(e)])
            return make_response(data, 400)
        except InvalidParametersError as e:
            data = serializer.encode([str(e)])
            return make_response(data, 400)
        except ElementAlreadyExistsError as e:
            data = serializer.encode([str(e)])
            return make_response(data, 400)
        except ValueError:
            data = serializer.encode(["No parsable data in the request"])
            return make_response(data, 400)
        except ElementNotExistsError:
            return make_response('', 404)
        except HTTPException:
            raise
        except Exception as e:
            return make_response(serializer.encode([str(e)]), 500)
    return decorated_func
