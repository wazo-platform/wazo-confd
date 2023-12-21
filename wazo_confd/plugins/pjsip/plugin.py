# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from . import schema
from .resource import (
    PJSIPDocList,
    PJSIPGlobalList,
    PJSIPSystemList,
    PJSIPTransportItem,
    PJSIPTransportList,
)
from .service import build_pjsip_transport_service, build_service

logger = logging.getLogger(__name__)


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        pjsip_doc = dependencies['pjsip_doc']

        service = build_service(pjsip_doc)
        transport_service = build_pjsip_transport_service(
            pjsip_doc, schema.PJSIPTransportSchema()
        )

        api.add_resource(
            PJSIPDocList,
            '/asterisk/pjsip/doc',
            resource_class_args=(pjsip_doc,),
        )

        api.add_resource(
            PJSIPGlobalList,
            '/asterisk/pjsip/global',
            resource_class_args=(service,),
        )

        api.add_resource(
            PJSIPSystemList,
            '/asterisk/pjsip/system',
            resource_class_args=(service,),
        )

        api.add_resource(
            PJSIPTransportList,
            '/sip/transports',
            resource_class_args=(transport_service,),
        )

        api.add_resource(
            PJSIPTransportItem,
            '/sip/transports/<uuid:transport_uuid>',
            endpoint='sip_transports',
            resource_class_args=(transport_service,),
        )
