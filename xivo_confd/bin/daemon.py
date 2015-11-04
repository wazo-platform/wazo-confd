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

import logging
import sys

from xivo.daemonize import pidfile_context
from xivo.user_rights import change_user
from xivo import xivo_logging

from xivo_confd.config import load as load_config
from xivo_confd.controller import Controller


logger = logging.getLogger(__name__)


def main(argv):
    config = load_config(argv)

    xivo_logging.setup_logging(config['log_filename'], config['foreground'],
                               config['debug'], config['log_level'])
    xivo_logging.silence_loggers(['Flask-Cors'], logging.WARNING)

    if config['user']:
        change_user(config['user'])

    controller = Controller(config)

    with pidfile_context(config['pid_filename'], config['foreground']):
        controller.run()


if __name__ == '__main__':
    main(sys.argv[1:])
