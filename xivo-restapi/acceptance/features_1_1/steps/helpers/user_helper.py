from xivo_dao.data_handler.line import dao as line_dao
from xivo_dao.data_handler.user import dao as user_dao
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.exception import ElementNotExistsError

from xivo_dao import extensions_dao, extenumber_dao, queue_member_dao, \
    rightcall_member_dao, callfilter_dao, dialaction_dao, phonefunckey_dao, \
    schedule_dao, voicemail_dao


def delete_all():
    for user in user_dao.find_all():
        user_dao.delete(user)


def create_user(userinfo):
    user = User(**userinfo)
    user_dao.create(user)


def assert_user_deleted(userid):
    _check_user_features(userid)
#    _check_queuemembers(userid)
    _check_rightcallmembers(userid)
    _check_callfiltermember(userid)
    _check_dialaction(userid)
    _check_phonefunckey(userid)
    _check_schedulepath(userid)
    _check_contextmember(userid)
    _check_voicemail(userid)


def _check_user_features(userid):
    try:
        user_dao.get(userid)
        assert False, "user was not deleted from table userfeatures"
    except ElementNotExistsError:
        assert True


def _check_extensions(userid):
    assert extensions_dao.get_by_exten(userid) is None


def _check_extenumbers(userid):
    assert extenumber_dao.get_by_exten(userid) is None


def _check_contextnummembers(userid):
    assert line_dao.get_contextnummember(userid) is None


#def _check_queuemembers():
#    if hasattr(world, 'interface'):
#        result = queue_member_dao.get_queue_members_for_queues()
#        processed_result = [item.member_name for item in result if item.member_name == world.interface]
#        assert processed_result == [], str(processed_result)


def _check_rightcallmembers(userid):
    result = rightcall_member_dao.get_by_userid(userid)
    assert result == []


def _check_callfiltermember(userid):
    result = callfilter_dao.get_callfiltermembers_by_userid(userid)
    assert result == []


def _check_dialaction(userid):
    result = dialaction_dao.get_by_userid(userid)
    assert result == []


def _check_phonefunckey(userid):
    result = phonefunckey_dao.get_by_userid(userid)
    assert result == []


def _check_schedulepath(userid):
    result = schedule_dao.get_schedules_for_user(userid)
    assert result == []


def _check_contextmember(userid):
    result = voicemail_dao.get_contextmember(userid)
    assert result is None, result


def _check_voicemail(userid):
    assert voicemail_dao.get(userid) is None
