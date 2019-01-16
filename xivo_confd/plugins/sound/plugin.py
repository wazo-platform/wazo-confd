# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_confd.helpers.ari import Client as ARIClient

from .resource import SoundItem, SoundList, SoundFileItem
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        ari_client = ARIClient(**config['ari'])
        service = build_service(ari_client)

        api.add_resource(
            SoundList,
            '/sounds',
            resource_class_args=(service,)
        )

        api.add_resource(
            SoundItem,
            '/sounds/<filename:category>',
            endpoint='sounds',
            resource_class_args=(service,)
        )

        api.add_resource(
            SoundFileItem,
            '/sounds/<filename:category>/files/<filename:filename>',
            endpoint='soundsfileitem',
            resource_class_args=(service,)
        )
