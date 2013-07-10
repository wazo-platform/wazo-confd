from acceptance.features_1_1 import ws_utils_session as ws_utils


def all_users():
    return ws_utils.rest_get('users/')


def get_user(userid):
    return ws_utils.rest_get('users/%s' % userid)


def create_user(properties):
    return ws_utils.rest_post('users/', properties)


def update_user(userid, properties):
    return ws_utils.rest_put('users/%s' % userid, properties)


def delete_user(userid):
    return ws_utils.rest_delete('users/%s' % userid)
