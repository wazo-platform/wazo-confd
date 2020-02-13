# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import gzip
import json

from .service import build_service
from .resource import PJSIPDocList, PJSIPGlobalList
from .exceptions import PJSIPDocError

logger = logging.getLogger(__name__)


class PJSIPDoc:
    def __init__(self, filename):
        logger.debug('%s initialized with file %s', self.__class__.__name__, filename)
        self._filename = filename

    def get(self):
        try:
            with gzip.open(self._filename, 'rb') as f:
                return json.load(f)
        except Exception as e:
            logger.info('failed to read PJSIP doc %s %s', self._filename, e)
            raise PJSIPDocError('failed to read PJSIP JSON documentation')


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']

        pjsip_doc = PJSIPDoc(config['pjsip_config_doc_filename'])
        service = build_service(pjsip_doc)

        api.add_resource(
            PJSIPDocList, '/asterisk/pjsip/doc', resource_class_args=(pjsip_doc,),
        )

        api.add_resource(
            PJSIPGlobalList, '/asterisk/pjsip/global', resource_class_args=(service,),
        )
