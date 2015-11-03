import logging

from kombu import Connection, Exchange, Producer
from xivo_bus import Marshaler

logger = logging.getLogger(__name__)


class BusPublisher(object):

    @classmethod
    def from_config(cls, config):
        url = 'amqp://{username}:{password}@{host}:{port}//'.format(**config['bus'])
        exchange_name = config['bus']['exchange_name']
        exchange_type = config['bus']['exchange_type']
        uuid = config['uuid']
        return cls(url, exchange_name, exchange_type, uuid)

    def __init__(self, url, exchange_name, exchange_type, uuid):
        self.url = url
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.uuid = uuid
        self.messages = []

    def send_bus_event(self, message, routing_key):
        self.publish(message, routing_key)

    def publish(self, message, routing_key):
        self.messages.append((message, routing_key))

    def flush(self):
        exchange = Exchange(self.exchange_name, self.exchange_type)
        marshaler = Marshaler(self.uuid)
        with Connection(self.url) as connection:
            producer = Producer(connection, exchange=exchange, auto_declare=True)
            publish = connection.ensure(producer, producer.publish,
                                        errback=self.publish_error, max_retries=3,
                                        interval_start=1)
            self.send_messages(marshaler, publish)

    def send_messages(self, marshaler, publish):
        for event, routing_key in self.messages:
            message = marshaler.marshal_message(event)
            publish(message, routing_key=routing_key)

    def publish_error(self, exc, interval):
        logger.error('Error: %s', exc, exc_info=1)
        logger.info('Retry in %s seconds...', interval)
