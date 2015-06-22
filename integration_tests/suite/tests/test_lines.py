from test_api import config

from test_api import confd
from test_api import fixtures
from test_api import scenarios as s
from test_api import errors as e
from test_api.helpers.line import generate_line


REQUIRED = ['context', 'device_slot']

BOGUS = [('context', 123, 'unicode string'),
         ('device_slot', '1', 'integer'),
         ('device_slot', 0, 'positive numeric')]


class TestLineResource(s.GetScenarios, s.CreateScenarios, s.EditScenarios, s.DeleteScenarios):

    url = "/lines_sip"
    resource = "Line"
    required = REQUIRED
    bogus_fields = BOGUS

    def create_resource(self):
        line = generate_line()
        return line['id']

    def post_resource(self, parameters):
        parameters.setdefault('context', config.CONTEXT)
        return confd.lines_sip.post(parameters)


def test_create_line_with_fake_context():
    response = confd.lines_sip.post(context='fakecontext',
                                      device_slot=1)
    response.assert_match(400, e.not_found('Context'))


@fixtures.line()
def test_edit_line_with_fake_context(line):
    response = confd.lines_sip(line['id']).put(context='fakecontext',
                                                 device_slot=1)
    response.assert_match(400, e.not_found('Context'))
