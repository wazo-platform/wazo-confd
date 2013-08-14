from acceptance.features_1_1 import ws_utils_session as ws_utils

USERS_URL = 'users'


def all_users():
    return ws_utils.rest_get(USERS_URL)


def all_users_with_voicemail():
    return ws_utils.rest_get('%s/?include=voicemail' % USERS_URL)


def get_lines_associated_to_a_user(userid):
    return ws_utils.rest_get('%s/%s/user_links' % (USERS_URL, userid))


def get_user(userid):
    return ws_utils.rest_get('%s/%s' % (USERS_URL, userid))


def get_user_with_voicemail(userid):
    params = {'include': 'voicemail'}
    return ws_utils.rest_get('%s/%s' % (USERS_URL, userid), params=params)


def user_search(search):
    params = {'q': search}
    return ws_utils.rest_get(USERS_URL, params=params)


def create_user(parameters):
    return ws_utils.rest_post(USERS_URL, parameters)


def update_user(userid, parameters):
    return ws_utils.rest_put('%s/%s' % (USERS_URL, userid), parameters)


def delete_user(userid):
    return ws_utils.rest_delete('%s/%s' % (USERS_URL, userid))
