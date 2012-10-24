

from gevent import httplib

from recording_config import RecordingConfig
from cti_protocol import CtiProtocol


class RestCampaign(object):

    def create(self, campaign_name):
        connection = httplib.HTTPConnection(RecordingConfig.XIVO_RECORD_SERVICE_ADDRESS + ":" + str(RecordingConfig.XIVO_RECORD_SERVICE_PORT))
        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/" + campaign_name
        body_content = """{"test":{"id": "6", "name": "jirka"}}"""
        body = CtiProtocol.encode(body_content)
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        print("body: " + body)

        connection.request("POST", requestURI, body, headers)

        reply = connection.getresponse()
        print("reply: " + reply.read())
        replyHeader = reply.getheaders()
        print("replyHeader: " + str(replyHeader))


        #assert rHeader ==

        return False
