# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

import logging
import xivo_dao

from functools import partial

from xivo.consul_helpers import ServiceCatalogRegistration
from xivo_confd import setup_app
from xivo_confd.server import run_server

from .service_discovery import self_check

logger = logging.getLogger(__name__)


class Controller(object):
    def __init__(self, config):
        self.config = config

    def run(self):
        logger.debug('xivo-confd running...')

        xivo_dao.init_db_from_config(self.config)

        app = setup_app(self.config)

        with ServiceCatalogRegistration('xivo-confd',
                                        self.config['uuid'],
                                        self.config['consul'],
                                        self.config['service_discovery'],
                                        self.config['bus'],
                                        partial(self_check, self.config)):
            run_server(app)
