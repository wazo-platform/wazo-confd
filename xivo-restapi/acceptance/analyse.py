#!/usr/bin/env python2

import sys
import traceback
from httplib2 import Http
from json import dumps, loads
import inspect

URI_BASE = "https://192.168.32.186:50051/1.1"
FAIL_COLOR = '\033[91m'
END_COLOR = '\033[0m'
HEADER_COLOR = '\033[95m'
PASS_COLOR = '\033[92m'


h = Http(disable_ssl_certificate_validation=True)
headers = {'Content-type': 'application/json'}


def handle_test(function):
    def handleProblems():
        try:
            function()

        except AssertionError:
            tb = sys.exc_info()[-1]
            tbInfo = traceback.extract_tb(tb)
            filename, line, func, text = tbInfo[-1]
            failed_message = 'FAILED TEST on line ' + str(line) + ' (' + func + ')' + ' in statement ' + text
            splitter = len(failed_message) * '='
            print("%s\n%s\n%s\n%s" % (FAIL_COLOR, failed_message, splitter, END_COLOR))
            handle_test.failed_tests += 1
        #else:
        #    message = "Test passed!"
        #    splitter = len(message) * '='
        #    print ("\n%s%s\n%s\n%s" % (PASS_COLOR, message, splitter, END_COLOR))

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
    resp, content = h.request(URI_BASE + "/users/", "POST", headers=headers,  body=dumps(data))
    new_user_id = loads(content)['id']

    data = dict(context="default")
    resp, content = h.request(URI_BASE + "/lines_sip/", "POST", headers=headers,  body=dumps(data))
    new_line_id = loads(content)['id']

    data = dict(user_id=new_user_id, line_id=new_line_id, extension_id="999999999")
    resp, content = h.request(URI_BASE + "/user_links/", "POST", headers=headers,  body=dumps(data))
    _print_result(resp, content)

    assert(resp['status'] == '400')


def _print_result(resp, content):
    caller_name = inspect.stack()[1][3]
    splitter = '-' * 120
    print ("%s%s\n%s\n%s%s\n%s\n%s" % (HEADER_COLOR, splitter, caller_name, splitter, END_COLOR, resp, content))


def _print_failed_tests(count):
    failed_message = "%s TESTS FAILED" % (count)
    splitter = 120 * '='
    print ("%s\n%s\n%s\n%s%s" % (FAIL_COLOR, splitter, failed_message, splitter, END_COLOR))


if __name__ == "__main__":
    handle_test.failed_tests = 0
    print "Running Acceptance tests on REST API"

    #test_list_lines()
    #test_create_empty_sip_line()
    #test_create_line_empty_context()
    #test_create_line_fake_context()
    #test_create_line_invalid_params()
    #test_create_line_with_context()
    #test_create_line_with_context_not_default()
    #test_create_2_lines_same_context()
    #test_create_empty_link()
    #test_create_link_empty_params()
    #test_create_link_invalid_values()
    #test_create_link_invalid_params()
    #test_create_link_missing_lineid()
    test_create_link_unexisting_extension()

    _print_failed_tests(handle_test.failed_tests)
