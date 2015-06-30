from test_api import confd
from contextlib import contextmanager


def associate(user_id, line_id):
    response = confd.users(user_id).lines.post(line_id=line_id)
    response.assert_ok()


def dissociate(user_id, line_id):
    response = confd.users(user_id).lines(line_id).delete()
    response.assert_ok()


@contextmanager
def user_and_line_associated(user, line):
    associate(user['id'], line['id'])
    yield
    dissociate(user['id'], line['id'])
