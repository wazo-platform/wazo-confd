'''
Created on Oct 1, 2012

@author: jirih
'''
import unittest
from mock import Mock
from xivo_recording.http_server import HttpServer


class TestHttpServer(unittest.TestCase):

    def setUp(self):
        self.http_server = HttpServer(5999)

    def test_create_named_campaign_monoqueue(self):
        response = Mock()

        status = '200 OK'
        headers = [
            ('Content-Type', 'application/json')
        ]

        response.assert_called_with(status, headers)
