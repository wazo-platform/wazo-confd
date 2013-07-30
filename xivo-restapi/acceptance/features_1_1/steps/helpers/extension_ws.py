from acceptance.features_1_1 import ws_utils_session as ws_utils


def all_extensions():
    return ws_utils.rest_get('extensions/')
