from helpers.remote import remote_exec

from xivo_dao.data_handler.user import dao as user_dao


def delete_all():
    remote_exec(_delete_all)


def _delete_all(channel):
    from xivo_dao.data_handler.user import services as user_services
    from xivo_dao.data_handler.user_line_extension import services as ule_services

    for user in user_services.find_all():

        ules = ule_services.find_all_by_user_id(user.id)
        for ule in ules:
            ule_services.delete(ule)

        user_services.delete(user)


def create_user(userinfo):
    remote_exec(_create_user, userinfo=userinfo)


def _create_user(channel, userinfo):
    from xivo_dao.data_handler.user import services as user_services
    from xivo_dao.data_handler.user.model import User

    user = User(**userinfo)
    user_services.create(user)


def find_user_by_name(name):
    firstname, lastname = name.split(" ")
    return user_dao.find_user(firstname, lastname)
