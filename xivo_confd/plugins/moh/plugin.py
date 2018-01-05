# -*- coding: UTF-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.server import add_endpoint_to_do_not_log_data_list

from .resource import MohItem, MohList, MohFileItem
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            MohList,
            '/moh',
            resource_class_args=(service,)
        )

        api.add_resource(
            MohItem,
            '/moh/<uuid>',
            endpoint='moh',
            resource_class_args=(service,)
        )

        api.add_resource(
            MohFileItem,
            '/moh/<uuid>/files/<filename:filename>',
            endpoint='mohfileitem',
            resource_class_args=(service,)
        )
        add_endpoint_to_do_not_log_data_list('mohfileitem')
