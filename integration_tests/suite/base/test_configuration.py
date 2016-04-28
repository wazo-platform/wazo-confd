import unittest

from test_api import confd
from test_api import errors as e


class TestConfiguration(unittest.TestCase):

    def test_live_reload_missing_parameters(self):
        response = confd.configuration.live_reload.put()
        response.assert_match(400,
                              e.missing_parameters('enabled'))

    def test_live_reload_invalid_parameters(self):
        response = confd.configuration.live_reload.put(enabled=True,
                                                       toto='tata')
        response.assert_match(400,
                              e.unknown_parameters('toto'))
