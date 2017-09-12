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

    def send_bus_event(self, message, routing_key, headers=None):
        self.publish(message, routing_key, headers)

    def publish(self, message, routing_key, headers=None):
        self.messages.append((message, routing_key, headers))

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
        for event, routing_key, headers in self.messages:
            message = marshaler.marshal_message(event)
            all_headers = dict(marshaler.metadata(event))
            all_headers.update(headers or {})
            publish(message, content_type=marshaler.content_type, routing_key=routing_key, headers=all_headers)

    def publish_error(self, exc, interval):
        logger.error('Error: %s', exc, exc_info=1)
        logger.info('Retry in %s seconds...', interval)

    def rollback(self):
        self.messages = []
