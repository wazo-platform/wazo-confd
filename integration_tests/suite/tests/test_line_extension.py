from test_api.helpers.line import generate_line, delete_line
from test_api.helpers.extension import generate_extension, delete_extension
from test_api.helpers.line_extension import line_and_extension_associated as association
from test_api.helpers.line_device import line_and_device_associated as l_d_association
from test_api import scenarios as s
from test_api import errors as e
from test_api import confd
from test_api import fixtures

from hamcrest import assert_that, contains, has_entries

import re


FAKE_ID = 999999999

no_line_associated_regex = re.compile(r"Extension with id=\d+ does not have a line")
no_user_associated_regex = re.compile(r"line with id \d+ is not associated to a user")
already_associated_regex = re.compile(r"line with id \d+ already has an extension with a context of type 'internal'")


class TestLineExtensionCollectionAssociation(s.AssociationScenarios, s.DissociationCollectionScenarios, s.AssociationGetCollectionScenarios):

    left_resource = "Line"
    right_resource = "Extension"

    def create_resources(self):
        line = generate_line()
        extension = generate_extension()
        return line['id'], extension['id']

    def delete_resources(self, line_id, extension_id):
        delete_line(line_id)
        delete_extension(extension_id)

    def associate_resources(self, line_id, extension_id):
        return confd.lines(line_id).extensions.post(extension_id=extension_id)

    def dissociate_resources(self, line_id, extension_id):
        return confd.lines(line_id).extensions(extension_id).delete()

    def get_association(self, line_id, extension_id):
        return confd.lines(line_id).extensions.get()


class TestLineExtensionAssociation(s.AssociationScenarios, s.DissociationScenarios, s.AssociationGetScenarios):

    left_resource = "Line"
    right_resource = "Extension"

    def create_resources(self):
        line = generate_line()
        extension = generate_extension()
        return line['id'], extension['id']

    def delete_resources(self, line_id, extension_id):
        delete_line(line_id)
        delete_extension(extension_id)

    def associate_resources(self, line_id, extension_id):
        return confd.lines(line_id).extension.post(extension_id=extension_id)

    def dissociate_resources(self, line_id, extension_id):
        return confd.lines(line_id).extension.delete()

    def get_association(self, line_id, extension_id):
        return confd.lines(line_id).extension.get()


@fixtures.line()
def test_get_associations_when_not_associated(line):
    response = confd.lines(line['id']).extensions.get()
    assert_that(response.items, contains())


@fixtures.line()
@fixtures.extension()
def test_get_line_from_extension_when_not_associated(line, extension):
    response = confd.extensions(extension['id']).line.get()
    response.assert_match(404, e.not_found('LineExtension'))


def test_get_line_from_fake_extension():
    response = confd.extensions(FAKE_ID).line.get()
    response.assert_match(404, e.not_found('Extension'))


@fixtures.line()
@fixtures.extension()
def test_associate_line_and_internal_extension(line, extension):
    expected = has_entries({'line_id': line['id'],
                            'extension_id': extension['id']})

    response = confd.lines(line['id']).extensions.post(extension_id=extension['id'])
    assert_that(response.item, expected)


@fixtures.extension('from-extern')
@fixtures.line()
def test_associate_incall_to_line_without_user(incall, line):
    response = confd.lines(line['id']).extensions.post(extension_id=incall['id'])
    response.assert_match(400, e.missing_association('Line', 'User'))


@fixtures.extension()
@fixtures.extension()
@fixtures.line()
def test_associate_two_internal_extensions_to_same_line(first_extension, second_extension, line):
    associate = confd.lines(line['id']).extensions

    response = associate.post(extension_id=first_extension['id'])
    response.assert_status(201)

    response = associate.post(extension_id=second_extension['id'])
    response.assert_match(400, e.resource_associated('Line', 'Extension'))


@fixtures.line()
@fixtures.extension()
def test_dissociate_line_and_extension(line, extension):
    with association(line, extension, check=False):
        response = confd.lines(line['id']).extensions(extension['id']).delete()
        response.assert_ok()


@fixtures.line()
@fixtures.extension()
@fixtures.device()
def test_dissociate_line_associated_to_a_device(line, extension, device):
    with association(line, extension), l_d_association(line, device):
        response = confd.lines(line['id']).extensions(extension['id']).delete()
        response.assert_status(400, e.resource_associated('Line', 'Device'))


@fixtures.line()
@fixtures.extension()
def test_delete_extension_associated_to_line(line, extension):
    with association(line, extension):
        response = confd.extensions(extension['id']).delete()
        response.assert_match(400, e.resource_associated('Extension', 'Line'))
