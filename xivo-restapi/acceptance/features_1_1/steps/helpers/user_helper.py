from xivo_dao.data_handler.user import dao as user_dao
from xivo_dao.data_handler.user.model import User


def delete_all():
    for user in user_dao.find_all():
        user_dao.delete(user)


def create_user(userinfo):
    user = User(**userinfo)
    user_dao.create(user)
