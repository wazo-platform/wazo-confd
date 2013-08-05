#!/usr/bin/env python2

import sys
import traceback
from httplib2 import Http
from json import dumps, loads
import argparse

FAIL_COLOR = '\033[91m'
END_COLOR = '\033[0m'
HEADER_COLOR = '\033[95m'
PASS_COLOR = '\033[92m'


h = Http(disable_ssl_certificate_validation=True)
headers = {'Content-type': 'application/json'}


def handle_test(function):
    def handleProblems():
        try:
            caller_name = function.__name__
            splitter = '-' * 120
            print ("%s%s\n%s\n%s%s\n" % (HEADER_COLOR, splitter, caller_name, splitter, END_COLOR))
            function()

        except AssertionError:
            tb = sys.exc_info()[-1]
            tbInfo = traceback.extract_tb(tb)
            filename, line, func, text = tbInfo[-1]
            failed_message = 'FAILED TEST on line ' + str(line) + ' (' + func + ')' + ' in statement ' + text
            splitter = len(failed_message) * '='
            print("%s\n%s\n%s\n%s" % (FAIL_COLOR, failed_message, splitter, END_COLOR))
            handle_test.failed_tests += 1

    return handleProblems


@handle_test
def test_create_empty_sip_line():
    data = dict()
    resp, content = h.request(URI_BASE + "/lines_sip/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)
    assert(resp['status'] == '400')


@handle_test
def test_create_line_empty_context():
    data = dict(context="")
    resp, content = h.request(URI_BASE + "/lines_sip/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)
    assert(resp['status'] == '400')


@handle_test
def test_create_line_fake_context():
    data = dict(context="superdupercontext")
    resp, content = h.request(URI_BASE + "/lines_sip/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)

    assert(resp['status'] == '400')


@handle_test
def test_create_line_invalid_params():
    data = dict(context="default", invalidparameter="invalidvalue")
    resp, content = h.request(URI_BASE + "/lines_sip/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)
    assert(resp['status'] == '400')


@handle_test
def test_create_line_with_context():
    data = dict(context="default")
    resp, content = h.request(URI_BASE + "/lines_sip/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)
    assert(resp['status'] == '201')


@handle_test
def test_create_line_with_context_not_default():
    data = dict(context="statscenter")
    resp, content = h.request(URI_BASE + "/lines_sip/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)

    assert(resp['status'] == '201')


@handle_test
def test_list_lines():
    resp, content = h.request(URI_BASE + "/lines/", "GET", headers=headers)
    _print_result(resp, content)


@handle_test
def test_create_2_lines_same_context():
    data = dict(context="default")
    resp, content = h.request(URI_BASE + "/lines_sip/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)
    assert(resp['status'] == '201')
    resp, content = h.request(URI_BASE + "/lines_sip/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)

    assert(resp['status'] == '201')


@handle_test
def test_create_empty_link():
    data = dict()
    resp, content = h.request(URI_BASE + "/user_links/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)

    assert(resp['status'] == '400')
    assert("Missing parameter" in content)


@handle_test
def test_create_link_empty_params():
    data = dict(user_id="", extension_id="", line_id="")
    resp, content = h.request(URI_BASE + "/user_links/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)

    assert(resp['status'] == '400')


@handle_test
def test_create_link_invalid_values():
    data = dict(user_id="asdf", extension_id="1", line_id="2")
    resp, content = h.request(URI_BASE + "/user_links/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)

    assert(resp['status'] == '400')


@handle_test
def test_create_link_invalid_params():
    data = dict(user_id="1", extension_id="2", line_id="3", invalid="invalid")
    resp, content = h.request(URI_BASE + "/user_links/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)

    assert(resp['status'] == '400')


@handle_test
def test_create_link_missing_lineid():
    data = dict(user_id="1", extension_id="2")
    resp, content = h.request(URI_BASE + "/user_links/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)

    assert(resp['status'] == '400')


@handle_test
def test_create_link_unexisting_extension():
    data = dict(firstname="toto")
    resp_p1, content_p1 = h.request(URI_BASE + "/users/", "POST", headers=headers,  body=dumps(data))
    new_user_id = loads(content_p1)['id']
    _print_result(resp_p1, content_p1)

    data = dict(context="default")
    resp_p2, content_p2 = h.request(URI_BASE + "/lines_sip/", "POST", headers=headers,  body=dumps(data))
    new_line_id = loads(content_p2)['id']
    _print_result(resp_p2, content_p2)

    data = dict(user_id=new_user_id, line_id=new_line_id, extension_id="999999999")
    resp, content = h.request(URI_BASE + "/user_links/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)

    _delete_user(new_user_id)
    _delete_line(new_line_id)

    assert(resp['status'] == '400')


@handle_test
def test_create_link_unexisting_line():
    data = dict(firstname="Greg")
    resp, content = h.request(URI_BASE + "/users/", "POST", headers=headers,  body=dumps(data))
    new_user_id = loads(content)['id']
    _print_result(resp, content)

    data = dict(exten="1000", context="default")
    resp, content = h.request(URI_BASE + "/extensions/", "POST", headers=headers,  body=dumps(data))
    new_extension_id = loads(content)['id']
    _print_result(resp, content)

    data = dict(user_id=new_user_id, line_id="999999999", extension_id=new_extension_id)
    resp, content = h.request(URI_BASE + "/user_links/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)

    _delete_user(new_user_id)
    _delete_extension(new_extension_id)

    assert(resp['status'] == '400')


@handle_test
def test_create_link_unexisting_user():
    assert("Not implemented" is True)


@handle_test
def test_create_link_default_context():
    data = dict(firstname="Greg")
    resp, content = h.request(URI_BASE + "/users/", "POST", headers=headers,  body=dumps(data))
    new_user_id = loads(content)['id']
    _print_result(resp, content)

    data = dict(context="default")
    resp, content = h.request(URI_BASE + "/lines_sip/", "POST", headers=headers,  body=dumps(data))
    new_line_id = loads(content)['id']
    _print_result(resp, content)

    data = dict(exten="1000", context="default")
    resp, content = h.request(URI_BASE + "/extensions/", "POST", headers=headers,  body=dumps(data))
    new_extension_id = loads(content)['id']
    _print_result(resp, content)

    data = dict(user_id=new_user_id, line_id=new_line_id, extension_id=new_extension_id)
    resp, content = h.request(URI_BASE + "/user_links/", "POST", headers=headers,  body=dumps(data))
    new_link_id = loads(content)['id']
    _print_result(resp, content)

    _delete_link(new_link_id)
    _delete_user(new_user_id)
    _delete_line(new_line_id)
    _delete_extension(new_extension_id)

    assert(resp['status'] == '201')
    assert(new_link_id)


@handle_test
def test_create_link_other_context():
    data = dict(firstname="Greg")
    resp, content = h.request(URI_BASE + "/users/", "POST", headers=headers,  body=dumps(data))
    new_user_id = loads(content)['id']
    _print_result(resp, content)

    data = dict(context="statscenter")
    resp, content = h.request(URI_BASE + "/lines_sip/", "POST", headers=headers,  body=dumps(data))
    new_line_id = loads(content)['id']
    _print_result(resp, content)

    data = dict(exten="1000", context="default")
    resp, content = h.request(URI_BASE + "/extensions/", "POST", headers=headers,  body=dumps(data))
    new_extension_id = loads(content)['id']
    _print_result(resp, content)

    data = dict(user_id=new_user_id, line_id=new_line_id, extension_id=new_extension_id)
    resp, content = h.request(URI_BASE + "/user_links/", "POST", headers=headers,  body=dumps(data))
    new_link_id = loads(content)['id']
    _print_result(resp, content)

    _delete_link(new_link_id)
    _delete_user(new_user_id)
    _delete_line(new_line_id)
    _delete_extension(new_extension_id)

    assert(resp['status'] == '201')
    assert(new_link_id)


def _print_result(resp, content):
    print ("%s\n%s\n" % (resp, content))


def _print_failed_tests(count):
    failed_message = "%s TESTS FAILED" % (count)
    splitter = 120 * '='
    print ("%s\n%s\n%s\n%s%s" % (FAIL_COLOR, splitter, failed_message, splitter, END_COLOR))


def _delete_link(link_id):
    resp, content = h.request("%s%s%s" % (URI_BASE, "/user_links/", link_id), "DELETE", headers=headers)


def _delete_user(user_id):
    resp, content = h.request("%s%s%s" % (URI_BASE, "/users/", user_id), "DELETE", headers=headers)


def _delete_line(line_id):
    resp, content = h.request("%s%s%s" % (URI_BASE, "/lines_sip/", line_id), "DELETE", headers=headers)


def _delete_extension(extension_id):
    resp, content = h.request("%s%s%s" % (URI_BASE, "/extensions/", extension_id), "DELETE", headers=headers)


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Analyse Rest API acceptance tests')
    parser.add_argument('xivo_host', help='IP or domain of target XiVO installation')

    args = parser.parse_args()
    URI_BASE = "https://%s:50051/1.1" % (args.xivo_host)

    handle_test.failed_tests = 0
    print "Running Acceptance tests on REST API"

    test_list_lines()
    test_create_empty_sip_line()
    test_create_line_empty_context()
    test_create_line_fake_context()
    test_create_line_invalid_params()
    test_create_line_with_context()
    test_create_line_with_context_not_default()
    test_create_2_lines_same_context()
    test_create_empty_link()
    test_create_link_empty_params()
    test_create_link_invalid_values()
    test_create_link_invalid_params()
    test_create_link_missing_lineid()
    test_create_link_unexisting_extension()
    test_create_link_unexisting_line()
    test_create_link_unexisting_user()
    test_create_link_default_context()
    test_create_link_other_context()

    _print_failed_tests(handle_test.failed_tests)
