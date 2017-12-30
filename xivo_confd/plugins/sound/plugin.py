# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.application import add_endpoint_to_do_not_log_data_list
from xivo_confd.helpers.ari import Client as ARIClient

from .resource import SoundItem, SoundList, SoundFileItem
from .service import build_service


class Plugin(object):

    def load(self, core):
        api = core.api
        ari_client = ARIClient(**core.config['ari'])
        service = build_service(ari_client)

        api.add_resource(
            SoundList,
            '/sounds',
            resource_class_args=(service,)
        )

        api.add_resource(
            SoundItem,
            '/sounds/<filename:name>',
            endpoint='sounds',
            resource_class_args=(service,)
        )

        api.add_resource(
            SoundFileItem,
            '/sounds/<filename:name>/files/<filename:filename>',
            endpoint='soundsfileitem',
            resource_class_args=(service,)
        )
        add_endpoint_to_do_not_log_data_list('soundsfileitem')
