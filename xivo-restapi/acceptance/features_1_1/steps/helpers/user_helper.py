from xivo_dao.data_handler.user import dao as user_dao
from xivo_dao.data_handler.user.model import User


def delete_all():
    for user in user_dao.find_all():
        user_dao.delete(user)


def create_user(userinfo):
    _delete_user_if_needed(userinfo)
    _create_user(userinfo)


def _delete_user_if_needed(userinfo):
    user = user_dao.find_user(userinfo['firstname'], userinfo['lastname'])
    if user:
        user_dao.delete(user)


def _create_user(userinfo):
    user = User(**userinfo)
    user_dao.create(user)


def find_user_by_name(name):
    firstname, lastname = name.split(" ")
    return user_dao.find_user(firstname, lastname)
