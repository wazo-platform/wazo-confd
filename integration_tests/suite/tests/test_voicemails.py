
from test_api import confd
from test_api import fixtures
from test_api import scenarios as s
from test_api import errors as e
from test_api.helpers.voicemail import generate_voicemail, generate_number_and_context


REQUIRED = ['name', 'number', 'context']

BOGUS = [
    ('name', 123, 'unicode string'),
    ('number', 123, 'unicode string'),
    ('number', 'fakenumber', 'numeric string'),
    ('context', 123, 'unicode string'),
    ('password', 123, 'unicode string'),
    ('password', 'fakepassword', 'numeric string'),
    ('password', 123, 'unicode string'),
    ('email', 123, 'unicode string'),
    ('language', 123, 'unicode string'),
    ('timezone', 123, 'unicode string'),
    ('max_messages', '3', 'integer'),
    ('attach_audio', 'true', 'boolean'),
    ('delete_messages', 'false', 'boolean'),
    ('ask_password', 'true', 'boolean')
]

FAKE = [
    ('context', 'wrongcontext', 'Context'),
    ('language', 'fakelanguage', 'Language'),
    ('timezone', 'faketimezone', 'Timezone')
]


class TestVoicemailResource(s.GetScenarios, s.CreateScenarios, s.EditScenarios, s.DeleteScenarios):

    url = "/voicemails"
    resource = "Voicemail"
    required = REQUIRED
    bogus_fields = BOGUS

    def create_resource(self):
        voicemail = generate_voicemail()
        return voicemail['id']

    def post_resource(self, parameters):
        fields = _generate_fields()
        fields.update(parameters)
        return confd.voicemails.post(fields)


def _generate_fields():
    number, context = generate_number_and_context()
    return {'number': number, 'context': context, 'name': 'testvoicemail'}


@fixtures.voicemail
def test_fake_fields(voicemail):
    requests = (confd.voicemails.post,
                confd.voicemails(voicemail['id']).put)

    for (field, value, error_field) in FAKE:
        for request in requests:
            fields = _generate_fields()
            fields[field] = value
            response = request(fields)
            yield response.assert_match, 400, e.not_found(error_field)


@fixtures.voicemail()
def test_create_voicemail_with_same_number_and_context(voicemail):
    response = confd.voicemails.post(name='testvoicemail',
                                       number=voicemail['number'],
                                       context=voicemail['context'])
    response.assert_match(400, e.resource_exists('Voicemail'))


@fixtures.voicemail()
@fixtures.voicemail()
def test_edit_voicemail_with_same_number_and_context(first_voicemail, second_voicemail):
    response = confd.voicemails(first_voicemail['id']).put(number=second_voicemail['number'],
                                                             context=second_voicemail['context'])
    response.assert_match(400, e.resource_exists('Voicemail'))
