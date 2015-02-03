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
import logging

from kombu import Connection, Exchange, Producer

from xivo.daemonize import pidfile_context
from xivo.user_rights import change_user
from xivo.xivo_logging import setup_logging
from xivo_bus import Marshaler

from xivo_confd.config import load as load_config
from xivo_confd.controller import Controller

logger = logging.getLogger(__name__)


def main(argv):
    config = load_config(argv)

    setup_logging(config['log_filename'], config['foreground'], config['debug'], config['log_level'])

    if config['user']:
        change_user(config['user'])

    _configure_xivo_dao(config)

    controller = Controller(config)

    with pidfile_context(config['pid_filename'], config['foreground']):
        controller.run()


def _configure_xivo_dao(config):
    def _on_bus_publish_error(exc, interval):
        logger.error('Error: %s', exc, exc_info=1)
        logger.info('Retry in %s seconds...', interval)

    bus_url = 'amqp://{username}:{password}@{host}:{port}//'.format(**config['bus'])
    bus_connection = Connection(bus_url)
    bus_exchange = Exchange(config['bus']['exchange_name'],
                            type=config['bus']['exchange_type'])
    bus_producer = Producer(bus_connection, exchange=bus_exchange, auto_declare=True)
    bus_publish_fn = bus_connection.ensure(bus_producer, bus_producer.publish,
                                           errback=_on_bus_publish_error, max_retries=3,
                                           interval_start=1)

    xivo_dao.install_bus_event_producer(bus_publish_fn, Marshaler())


if __name__ == '__main__':
    main(sys.argv[1:])
