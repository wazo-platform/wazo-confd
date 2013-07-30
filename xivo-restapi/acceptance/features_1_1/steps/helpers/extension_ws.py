from acceptance.features_1_1 import ws_utils_session as ws_utils


def all_extensions():
    return ws_utils.rest_get('extensions/')


def get_extension(extension_id):
    return ws_utils.rest_get('extensions/%s' % extension_id)


def create_extension(properties):
    return ws_utils.rest_post('extensions/', properties)
