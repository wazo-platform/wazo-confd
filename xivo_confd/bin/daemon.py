# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging
import sys

from xivo import xivo_logging
from xivo.config_helper import set_xivo_uuid, UUIDNotFound
from xivo.daemonize import pidfile_context
from xivo.user_rights import change_user

from xivo_confd.config import load as load_config
from xivo_confd.controller import Controller

logger = logging.getLogger(__name__)

FOREGROUND = True  # Always in foreground systemd takes care of daemonizing


def main(argv=None):
    argv = argv or sys.argv[1:]
    config = load_config(argv)

    xivo_logging.setup_logging(config['log_filename'], FOREGROUND, config['debug'], config['log_level'])
    xivo_logging.silence_loggers(['Flask-Cors'], logging.WARNING)

    if config['user']:
        change_user(config['user'])

    try:
        set_xivo_uuid(config, logger)
    except UUIDNotFound:
        if config['service_discovery']['enabled']:
            raise

    controller = Controller(config)

    with pidfile_context(config['pid_filename'], FOREGROUND):
        controller.run()
