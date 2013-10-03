# -*- coding: UTF-8 -*-

import logging
from flask.blueprints import Blueprint
from flask.helpers import make_response
from xivo_restapi import config
from xivo_restapi.helpers.route_generator import RouteGenerator
from xivo_restapi.helpers.formatter import Formatter
from xivo_restapi.resources.voicemails import mapper
from xivo_restapi.helpers import serializer
from xivo_dao.data_handler.voicemail.model import Voicemail
from xivo_dao.data_handler.voicemail import services as voicemail_services
from xivo_restapi.helpers.common import extract_find_parameters


logger = logging.getLogger(__name__)
blueprint = Blueprint('voicemails', __name__, url_prefix='/%s/voicemails' % config.VERSION_1_1)
route = RouteGenerator(blueprint)
formatter = Formatter(mapper, serializer, Voicemail)


@route('')
def list():
    find_parameters = extract_find_parameters()
    search_result = voicemail_services.find_all(**find_parameters)
    result = formatter.list_to_api(search_result.items, search_result.total)
    return make_response(result, 200)


@route('/<int:voicemailid>')
def get(voicemailid):
    voicemail = voicemail_services.get(voicemailid)
    result = formatter.to_api(voicemail)
    return make_response(result, 200)
