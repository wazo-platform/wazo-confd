import unittest

from test_api import confd
from test_api import errors as e

FAKE_ID = 999999999


class TestCtiProfile(unittest.TestCase):

    def test_fake_cti_profile(self):
        response = confd.cti_profiles(FAKE_ID).get()
        response.assert_match(404,
                              e.not_found('CtiProfile'))
