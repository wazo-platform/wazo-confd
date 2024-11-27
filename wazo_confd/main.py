# Copyright 2013-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import sys

from wazo import xivo_logging
from wazo.config_helper import set_xivo_uuid, UUIDNotFound
from wazo.user_rights import change_user

from wazo_confd.config import load as load_config
from wazo_confd.controller import Controller

logger = logging.getLogger(__name__)


def main(argv=None):
    argv = argv or sys.argv[1:]
    config = load_config(argv)

    xivo_logging.setup_logging(
        config['log_filename'],
        debug=config['debug'],
        log_level=config['log_level'],
    )
    xivo_logging.silence_loggers(['Flask-Cors'], logging.WARNING)
    xivo_logging.silence_loggers(['amqp'], logging.INFO)

    if config['user']:
        change_user(config['user'])

    try:
        set_xivo_uuid(config, logger)
    except UUIDNotFound:
        if config['service_discovery']['enabled']:
            raise

    controller = Controller(config)
    controller.run()
