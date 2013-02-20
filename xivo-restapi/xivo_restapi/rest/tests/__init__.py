from functools import wraps
from mock import patch, Mock
from xivo_restapi.rest.authentication import xivo_realm_digest
from xivo_restapi.rest.negotiate import flask_negotiate
from xivo_restapi.services.agent_management import AgentManagement
from xivo_restapi.services.campagne_management import CampagneManagement
from xivo_restapi.services.queue_management import QueueManagement
from xivo_restapi.services.recording_management import RecordingManagement
from xivo_restapi.services.user_management import UserManagement


def mock_basic_decorator(func):
    return func


def mock_parameterized_decorator(string):
    def decorated(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorated

xivo_realm_digest.realmDigest = Mock()
xivo_realm_digest.realmDigest.requires_auth.side_effect = mock_basic_decorator
flask_negotiate.consumes = Mock()
flask_negotiate.consumes.side_effect = mock_parameterized_decorator
flask_negotiate.produces = Mock()
flask_negotiate.produces.side_effect = mock_parameterized_decorator

patcher_queue = patch("xivo_restapi.rest." + \
                             "API_queues.QueueManagement")
mock_queue = patcher_queue.start()
instance_queue_management = Mock(QueueManagement)
mock_queue.return_value = instance_queue_management

patcher_agent = patch("xivo_restapi.rest." + \
                             "API_agents.AgentManagement")
mock_agent = patcher_agent.start()
instance_agent_management = Mock(AgentManagement)
mock_agent.return_value = instance_agent_management

patcher_campaigns = patch("xivo_restapi.rest." + \
                             "API_campaigns.CampagneManagement")
mock_campaign = patcher_campaigns.start()
instance_campaign_management = Mock(CampagneManagement)
mock_campaign.return_value = instance_campaign_management

patcher_recordings = patch("xivo_restapi.rest." + \
                             "API_recordings.RecordingManagement")
mock_recording = patcher_recordings.start()
instance_recording_management = Mock(RecordingManagement)
mock_recording.return_value = instance_recording_management

patcher_users = patch("xivo_restapi.rest." + \
                             "API_users.UserManagement")
mock_user = patcher_users.start()
instance_user_management = Mock(UserManagement)
mock_user.return_value = instance_user_management
