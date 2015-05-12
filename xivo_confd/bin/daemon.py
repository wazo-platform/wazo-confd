# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

import sys
import xivo_dao

from xivo.chain_map import ChainMap
from xivo.daemonize import pidfile_context
from xivo.user_rights import change_user
from xivo.xivo_logging import setup_logging
from xivo_confd.resources.infos import services as info_services

from xivo_confd.config import load as load_config
from xivo_confd.controller import Controller


def main(argv):
    config = load_config(argv)

    setup_logging(config['log_filename'], config['foreground'], config['debug'], config['log_level'])

    if config['user']:
        change_user(config['user'])

    xivo_dao.init_db_from_config(config)
    xivo_dao.init_bus_from_config(ChainMap(config, {'uuid': info_services.get().uuid}))

    controller = Controller(config)

    with pidfile_context(config['pid_filename'], config['foreground']):
        controller.run()


if __name__ == '__main__':
    main(sys.argv[1:])
