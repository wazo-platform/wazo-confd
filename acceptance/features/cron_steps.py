# -*- coding: utf-8 -*-
from commands import getoutput
from datetime import timedelta, datetime
from lettuce import step
import os

directory = None


@step(u'Given there is a directory "([^"]*)"')
def given_there_is_a_directory_group1(step, dirname):
    global directory
    directory = dirname
    exists = os.path.exists(dirname)
    list_dirs = []
    head = dirname
    while not exists:
        (head, tail) = os.path.split(head)
        list_dirs.append(tail)
        exists = os.path.exists(head)
    list_dirs.reverse()
    for folder in list_dirs:
        head += "/" + folder
        os.mkdir(head)
    assert os.path.exists(dirname), "Could not create the directory"


@step(u'Given there is a file "([^"]*)" created "([^"]*)" days ago')
def given_there_is_a_file_created_days_ago(step, filename, numdays):
    global directory
    tdelta = timedelta(days=int(numdays))
    d_avant = datetime.now() - tdelta
    filepath = directory + "/" + filename
    strd_avant = d_avant.strftime("%Y-%m-%d %H:%M:%S")
    command = "touch " + filepath + " -d " + '"' + strd_avant + '"'
    print("\ncommande: " + command + "\n")
    getoutput(command)
    assert os.path.exists(filepath), "The file could not be created"


@step(u'Given there is a file "([^"]*)" created today')
def given_there_is_a_file_created_today(step, filename):
    global directory
    filepath = directory + "/" + filename
    command = "touch " + filepath
    print("\ncommande: " + command + "\n")
    getoutput(command)
    assert os.path.exists(filepath), "The file could not be created"


@step(u'When I run the script "([^"]*)"')
def when_i_run_the_script(step, script):
    script_path = os.path.abspath(script)
    res = getoutput("sh " + script_path)
    print("\n" + res + "\n")
    assert True


@step(u'Then "([^"]*)" and "([^"]*)" are deleted')
def then_group1_and_group2_are_deleted(step, group1, group2):
    global directory
    assert not os.path.exists(directory + "/" + group1), group1 + " still exists."
    assert not os.path.exists(directory + "/" + group2), group2 + " still exists."


@step(u'Then "([^"]*)" and "([^"]*)" are not deleted')
def then_group1_and_group2_are_not_deleted(step, group1, group2):
    global directory
    assert os.path.exists(directory + "/" + group1), group1 + " does not exist."
    assert os.path.exists(directory + "/" + group2), group2 + " does not exist."
