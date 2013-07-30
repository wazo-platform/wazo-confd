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
    InvalidParametersError, ElementAlreadyExistsError, ElementNotExistsError, \
    ElementCreationError, ElementDeletionError, ElementEditionError
from functools import wraps

logger = logging.getLogger(__name__)


def exception_catcher(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MissingParametersError as e:
            data = serializer.encode([unicode(e)])
            return make_response(data, 400)
        except InvalidParametersError as e:
            data = serializer.encode([unicode(e)])
            return make_response(data, 400)
        except ElementAlreadyExistsError as e:
            data = serializer.encode([unicode(e)])
            return make_response(data, 400)
        except ValueError, e:
            data = serializer.encode(["No parsable data in the request, Be sure to send a valid JSON file"])
            return make_response(data, 400)
        except ElementCreationError, e:
            logger.error("error during creation: %s", e)
            return make_response("error during creation: %s" % e, 400)
        except ElementEditionError, e:
            logger.error("error during edition: %s", e)
            return make_response("error during edition: %s" % e, 400)
        except ElementDeletionError, e:
            logger.error("error during deletion: %s", e)
            return make_response("error during deletion: %s" % e, 400)
        except ElementNotExistsError, e:
            logger.error("error element not exist: %s", e)
            return make_response('', 404)
        except HTTPException:
            raise
        except Exception as e:
            logger.error("unexpected error during request: %s", e, exc_info=True)
            return make_response(serializer.encode([unicode(e)]), 500)
    return decorated_func
