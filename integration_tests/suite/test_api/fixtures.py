from wrappers import IsolatedAction

from helpers import line, line_sip, endpoint_sip, endpoint_sccp
from helpers.user import generate_user, delete_user
from helpers.extension import generate_extension, delete_extension
from helpers.device import generate_device, delete_device
from helpers.voicemail import generate_voicemail, delete_voicemail
from helpers.context import generate_context, delete_context
from helpers import user_import


class user(IsolatedAction):

    actions = {'generate': generate_user,
               'delete': delete_user}


class line(IsolatedAction):

    actions = {'generate': line.generate_line,
               'delete': line.delete_line}


class line_sip(IsolatedAction):

    actions = {'generate': line_sip.generate_line,
               'delete': line_sip.delete_line}


class sip(IsolatedAction):

    actions = {'generate': endpoint_sip.generate_sip,
               'delete': endpoint_sip.delete_sip}


class sccp(IsolatedAction):

    actions = {'generate': endpoint_sccp.generate_sccp,
               'delete': endpoint_sccp.delete_sccp}


class extension(IsolatedAction):

    actions = {'generate': generate_extension,
               'delete': delete_extension}


class device(IsolatedAction):

    actions = {'generate': generate_device,
               'delete': delete_device}


class voicemail(IsolatedAction):

    actions = {'generate': generate_voicemail,
               'delete': delete_voicemail}


class context(IsolatedAction):

    actions = {'generate': generate_context,
               'delete': delete_context}


class csv_entry(IsolatedAction):

    actions = {'generate': user_import.generate_entry}
