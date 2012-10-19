

from gevent import httplib
from tests.test_config import TestConfig
from xivo_cti_encoding_interface.cti_encoder_provider import CtiEncoderProvider

class RestCampaign(object):


    def create(self, campaign_name):
        connection = httplib.HTTPConnection(TestConfig.XIVO_RECORD_SERVICE_ADDRESS)
        requestURI = TestConfig.XIVO_REST_SERVICE_ROOT_PATH + TestConfig.XIVO_RECORDING_SERVICE_PATH + campaign_name + "/"
        body_content = ""
        body = CtiEncoderProvider.encoder.encode(body_content)
        headers = TestConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        print("body: " + body)

        connection.request("POST", requestURI, body, headers)

        reply = connection.getresponse()
        replyHeader = reply.getHeader()
        print("replyHeader: " + replyHeader)
        #assert rHeader ==

        return False
