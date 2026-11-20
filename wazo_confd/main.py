# Copyright 2013-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
import sys

from xivo import xivo_logging
from xivo.config_helper import UUIDNotFound, set_xivo_uuid
from xivo.user_rights import change_user

from wazo_confd.config import VALID_ROLES
from wazo_confd.config import load as load_config
from wazo_confd.controller import Controller

logger = logging.getLogger(__name__)


def main(argv=None):
    argv = argv or sys.argv[1:]
    try:
        config = load_config(argv)
    except ValueError as e:
        print(f'invalid configuration: {e}', file=sys.stderr)  # journald gets stderr
        sys.exit(os.EX_CONFIG)  # 78: matches RestartPreventExitStatus in the units

    xivo_logging.setup_logging(
        config['log_filename'],
        debug=config['debug'],
        log_level=config['log_level'],
    )
    xivo_logging.silence_loggers(['Flask-Cors'], logging.WARNING)
    xivo_logging.silence_loggers(['amqp'], logging.INFO)

    if set(config['roles']) != set(VALID_ROLES):
        logger.info('Starting wazo-confd with roles: %s', ', '.join(config['roles']))

    if config['user']:
        change_user(config['user'])

    try:
        set_xivo_uuid(config, logger)
    except UUIDNotFound:
        if config['service_discovery']['enabled']:
            raise

    controller = Controller(config)
    controller.run()
