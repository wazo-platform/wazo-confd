'''
Created on Jan 20, 2013

@author: jean
'''
from flask import request, helpers
from mock import patch, Mock
from xivo_recording.rest.API_campaigns import APICampaigns
import unittest


class Test(unittest.TestCase):

    def setUp(self):
        self.patcher_request = patch("flask.request")
        mock_patch_request = self.patcher_request.start()
        self.instance_request = Mock(request)
        mock_patch_request.return_value = self.instance_request

        self.patcher_helpers = patch("flask.helpers")
        mock_patch_helpers = self.patcher_helpers.start()
        self.instance_helpers = Mock(helpers)
        mock_patch_helpers.return_value = self.instance_helpers

        self.API_campaigns = APICampaigns()
        self.API_campaigns._campagne_manager = Mock()

        unittest.TestCase.setUp(self)

    def test_add_campaign(self):
        pass