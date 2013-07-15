from xivo_dao.data_handler.user import dao as user_dao
from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_lettuce.manager_ws import user_manager_ws, voicemail_manager_ws


def delete_all():
    for user in user_dao.find_all():
        _delete_line_if_needed(user)
        user_dao.delete(user)


def _delete_line_if_needed(user):
    try:
        line = line_dao.get_by_user_id(user.id)
        line_dao.delete(line)
    except ElementNotExistsError:
        pass


def create_user(userinfo):
    if 'line number' in userinfo or 'voicemail number' in userinfo:
        _create_user_with_old_ws(userinfo)
    else:
        user = User(**userinfo)
        user_dao.create(user)


def _create_user_with_old_ws(userinfo):
    voicemail_manager_ws.delete_voicemails_with_number(userinfo['voicemail number'])

    wsinfo = {
        'firstname': userinfo['firstname'],
        'lastname': userinfo['lastname'],
        'language': userinfo['language'],
        'line_number': userinfo['line number'],
        'line_context': userinfo.get('context', 'default'),
        'voicemail_name': '%s %s' % (userinfo['firstname'], userinfo['lastname']),
        'voicemail_number': userinfo['voicemail number'],
    }

    user_manager_ws.add_or_replace_user(wsinfo)


def find_user_by_name(name):
    firstname, lastname = name.split(" ")
    return user_dao.find_user(firstname, lastname)
