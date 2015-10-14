from test_api import scenarios as s
from test_api import errors as e
from test_api import associations as a
from test_api import fixtures
from test_api import confd

from test_api.helpers.device import generate_device

from hamcrest import assert_that, has_entry, none


BOGUS = [
    ('ip', 'aelkurxynsle', 'IP address'),
    ('mac', 'o374awic87anwc', 'MAC address'),
    ('sn', 123, 'unicode string'),
    ('vendor', 123, 'unicode string'),
    ('model', 123, 'unicode string'),
    ('version', 123, 'unicode string'),
    ('plugin', 123, 'unicode string'),
    ('description', 123, 'unicode string'),
    ('template_id', 123, 'unicode string'),
    ('options', 123, 'dict-like structure'),
]


class TestDeviceResource(s.GetScenarios, s.CreateScenarios, s.EditScenarios, s.DeleteScenarios):

    url = "/devices"
    resource = "Device"
    required = []
    bogus_fields = BOGUS

    def create_resource(self):
        device = generate_device()
        return device['id']


@fixtures.device()
def test_create_2_devices_with_same_mac(device):
    response = confd.devices.post(mac=device['mac'])
    response.assert_match(400, e.resource_exists('Device'))


def test_create_device_with_fake_plugin():
    response = confd.devices.post(plugin='superduperplugin')
    response.assert_match(400, e.not_found('Plugin'))


def test_create_device_with_fake_template():
    response = confd.devices.post(template_id='superdupertemplate')
    response.assert_match(400, e.not_found('DeviceTemplate'))


@fixtures.device()
@fixtures.device()
def test_edit_device_with_same_mac(first_device, second_device):
    response = confd.devices(first_device['id']).put(mac=second_device['mac'])
    response.assert_match(400, e.resource_exists('Device'))


@fixtures.device()
def test_edit_device_with_fake_plugin(device):
    response = confd.devices(device['id']).put(plugin='superduperplugin')
    response.assert_match(400, e.not_found('Plugin'))


@fixtures.device()
def test_edit_device_with_fake_template(device):
    response = confd.devices(device['id']).put(template_id='superdupertemplate')
    response.assert_match(400, e.not_found('DeviceTemplate'))


@fixtures.device()
@fixtures.line()
def test_associate_line_to_a_device(device, line):
    response = confd.devices(device['id']).associate_line(line['id']).get()
    response.assert_status(403)


@fixtures.device()
@fixtures.line()
def test_dissociate_line_to_a_device(device, line):
    response = confd.devices(device['id']).remove_line(line['id']).get()
    response.assert_status(403)


@fixtures.device()
@fixtures.line()
def test_reset_to_autoprov_device_associated_to_line(device, line):
    with a.line_device(line, device, check=False):
        response = confd.devices(device['id']).autoprov.get()
        response.assert_ok()

        response = confd.lines(line['id']).get()
        assert_that(response.item, has_entry('device_id', none()))
