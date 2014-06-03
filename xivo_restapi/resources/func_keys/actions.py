import logging

from flask import request, make_response

from xivo_restapi.helpers.formatter import Formatter
from xivo_restapi.resources.func_keys import mapper
from xivo_restapi.helpers import serializer
from xivo_restapi.helpers.common import extract_search_parameters
from xivo_dao.data_handler.func_key.model import FuncKey
from xivo_dao.data_handler.func_key import services as func_key_services


logger = logging.getLogger(__name__)
formatter = Formatter(mapper, serializer, FuncKey)


def list():
    search_parameters = extract_search_parameters(request.args)
    search_result = func_key_services.search(**search_parameters)
    result = formatter.list_to_api(search_result.items, search_result.total)
    return make_response(result, 200)


def get(func_key_id):
    func_key = func_key_services.get(func_key_id)
    result = formatter.to_api(func_key)
    return make_response(result, 200)
