import logging

from flask import request, make_response

from xivo_confd.helpers.common import extract_search_parameters
from xivo_dao.data_handler.func_key.model import FuncKey
from xivo_dao.data_handler.func_key import services as func_key_services

from xivo_confd.flask_http_server import content_parser
from xivo_confd.helpers.mooltiparse import Field, Int, Unicode

from xivo_confd.helpers.converter import Converter


logger = logging.getLogger(__name__)

document = content_parser.document(
    Field('id', Int()),
    Field('type', Unicode()),
    Field('destination', Unicode()),
    Field('destination_id', Unicode()),
)

converter = Converter.for_document(document, FuncKey)


def list():
    search_parameters = extract_search_parameters(request.args)
    search_result = func_key_services.search(**search_parameters)
    items = converter.encode_list(search_result.items, search_result.total)
    return make_response(items, 200)


def get(func_key_id):
    func_key = func_key_services.get(func_key_id)
    encoded_func_key = converter.encode(func_key)
    return make_response(encoded_func_key, 200)
