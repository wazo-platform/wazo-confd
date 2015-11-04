# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging

import xivo_dao

from xivo.chain_map import ChainMap

from xivo_dao.resources.infos import dao as info_dao
from xivo_dao.helpers.db_utils import session_scope

from xivo_confd import run as start_wsgi_server
from xivo_confd import setup_app

logger = logging.getLogger(__name__)


class Controller(object):
    def __init__(self, config):
        self.config = config

    def run(self):
        logger.debug('xivo-confd running...')

        xivo_dao.init_db_from_config(self.config)

        with session_scope():
            config = ChainMap(self.config, {'uuid': info_dao.get().uuid})

        app = setup_app(config)
        start_wsgi_server(app, config)
