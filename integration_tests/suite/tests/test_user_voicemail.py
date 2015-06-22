from contextlib import contextmanager

from test_api import scenarios as s
from test_api import helpers as h
from test_api import errors as e
from test_api import confd
from test_api import fixtures

from test_api.helpers.user_line import user_and_line_associated


@contextmanager
def user_and_voicemail_associated(user, voicemail):
    response = confd.users(user['id']).voicemail.post(voicemail_id=voicemail['id'])
    response.assert_ok()
    yield
    confd.users(user['id']).voicemail.delete()


class TestUserVoicemailAssociation(s.AssociationScenarios,
                                   s.DissociationScenarios,
                                   s.AssociationGetScenarios):

    left_resource = "User"
    right_resource = "Voicemail"

    def create_resources(self):
        self.user_id = h.user.generate_user()['id']
        self.line_id = h.line.generate_line()['id']
        h.user_line.associate(self.user_id, self.line_id)

        self.voicemail_id = h.voicemail.generate_voicemail()['id']
        return self.user_id, self.voicemail_id

    def delete_resources(self, user_id, voicemail_id):
        h.voicemail.delete_voicemail(self.voicemail_id)

        h.user_line.dissociate(self.user_id, self.line_id)
        h.user.delete_user(self.user_id)
        h.voicemail.delete_voicemail(self.voicemail_id)

    def associate_resources(self, user_id, voicemail_id):
        return confd.users(user_id).voicemail.post(voicemail_id=voicemail_id)

    def dissociate_resources(self, user_id, voicemail_id):
        return confd.users(user_id).voicemail.delete()

    def get_association(self, user_id, voicemail_id):
        return confd.users(user_id).voicemail.get()


@fixtures.user()
@fixtures.voicemail()
def test_associate_when_user_has_no_line(user, voicemail):
    response = confd.users(user['id']).voicemail.post(voicemail_id=voicemail['id'])
    response.assert_match(400, e.missing_association('User', 'Line'))


@fixtures.user()
@fixtures.line()
@fixtures.voicemail()
def test_associate_when_already_associated(user, line, voicemail):
    with user_and_line_associated(user, line), user_and_voicemail_associated(user, voicemail):
        response = confd.users(user['id']).voicemail.post(voicemail_id=voicemail['id'])
        response.assert_match(400, e.resource_associated('User', 'Voicemail'))


@fixtures.user()
def test_get_when_not_associated(user):
    response = confd.users(user['id']).voicemail.get()
    response.assert_match(404, e.not_found('UserVoicemail'))


@fixtures.user()
@fixtures.line()
@fixtures.voicemail()
def test_delete_user_when_still_associated(user, line, voicemail):
    with user_and_line_associated(user, line), user_and_voicemail_associated(user, voicemail):
        response = confd.users(user['id']).delete()
        response.assert_match(400, e.resource_associated('User', 'Voicemail'))


@fixtures.user()
@fixtures.line()
@fixtures.voicemail()
def test_delete_voicemail_when_still_associated(user, line, voicemail):
    with user_and_line_associated(user, line), user_and_voicemail_associated(user, voicemail):
        response = confd.voicemails(voicemail['id']).delete()
        response.assert_match(400, e.resource_associated('Voicemail', 'User'))


@fixtures.user()
@fixtures.line()
@fixtures.voicemail()
def test_edit_voicemail_when_still_associated(user, line, voicemail):
    with user_and_line_associated(user, line), user_and_voicemail_associated(user, voicemail):
        response = confd.voicemails(voicemail['id']).put(number='1234')
        response.assert_match(400, e.resource_associated('Voicemail', 'User'))
