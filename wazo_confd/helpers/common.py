# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from functools import wraps

from flask import g
from flask_restful.utils import http_status_message
from werkzeug.exceptions import HTTPException

from xivo import rest_api_helpers
from xivo_dao.helpers.db_manager import Session
from xivo_dao.helpers.exception import ServiceError, NotFoundError
from wazo_provd_client.exceptions import ProvdError

logger = logging.getLogger(__name__)

GENERIC_ERRORS = (ServiceError,)

NOT_FOUND_ERRORS = (NotFoundError,)


def handle_api_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NOT_FOUND_ERRORS as error:
            rollback()
            message = decode_and_log_error(error)
            return [message], 404
        except GENERIC_ERRORS as error:
            rollback()
            message = decode_and_log_error(error)
            return [message], 400
        except rest_api_helpers.APIException as error:
            rollback()
            if error.status_code >= 500:
                logger.error("%s: %s", error, error.details, exc_info=True)
            return [str(error)], error.status_code
        except ProvdError as error:
            rollback()
            return 'Provd client error: {}'.format(error), error.status_code
        except HTTPException as error:
            rollback()
            messages, code = extract_http_messages(error)
            decode_and_log_error(error)
            return messages, code
        except Exception as error:
            rollback()
            message = decode_and_log_error(error, exc_info=True)
            return ['Unexpected error: {}'.format(message)], 500

    return wrapper


def rollback():
    Session.rollback()

    sysconfd = g.get('sysconfd_publisher')
    if sysconfd:
        sysconfd.rollback()

    bus = g.get('bus_publisher')
    if bus:
        bus.rollback()


def decode_and_log_error(error, exc_info=False):
    error_message = str(error)
    logger.error(error_message, exc_info=exc_info)
    return error_message


def extract_http_messages(error):
    # we need to keep error messages compatible with API v1.1,
    # but flask-restful's error handling isn't flexible
    # enough to allow us to reformat its error messages.
    # So we attempt to extract the errors from the exception

    # The `data` property is added by flask-restful
    # It contains all kwargs passed to the `abort` command
    # (e.i. abort(400, message={'key': 'value'})
    data = getattr(error, 'data', {})
    message = data.get('message', None)
    if isinstance(message, dict):
        code = error.code
        messages = [
            "Input Error - {}: {}".format(key, value) for key, value in message.items()
        ]
    elif isinstance(message, str):
        code = error.code
        messages = [message]
    else:
        # Return a generic HTTP error message if we couldn't find anything
        code = getattr(error, 'code', 400)
        messages = [getattr(error, 'description', http_status_message(code))]

    return messages, code
