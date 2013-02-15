# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..
from acceptance.features.cron_utils import create_dir
from acceptance.features.rest_campaign import RestCampaign
from commands import getoutput
from datetime import timedelta, datetime
from lettuce import step
from xivo_dao import recordings_dao
import os

directory = None


@step(u'Given there is a directory "([^"]*)"')
def given_there_is_a_directory_group1(step, dirname):
    global directory
    directory = dirname
    create_dir(dirname)
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


@step(u'Given there is a recording with id "([^"]*)" created "([^"]*)" days ago with campaign "([^"]*)" and agent "([^"]*)"')
def given_there_is_a_recording_with_id_group1_created_group2_days_ago_with_campaign_group3(step, rec_id, numdays, camp_id, agent_no):
    rest_campaign = RestCampaign()
    time = datetime.now()
    tdelta = timedelta(days=int(numdays))
    time = time - tdelta
    assert rest_campaign.addRecordingDetails(camp_id, rec_id,
                                             '2002', agent_no, time.strftime("%Y-%m-%d %H:%M:%S")), "Could not create the recording"


@step(u'Then items "([^"]*)" and "([^"]*)" are deleted from the database')
def then_items_group1_and_group2_are_deleted(step, group1, group2):
    results = recordings_dao.get_all()
    results_id = [item.cid for item in results]
    assert(group1 not in results_id)
    assert(group2 not in results_id)


@step(u'Then items "([^"]*)" and "([^"]*)" are not deleted from the database')
def then_items_group1_and_group2_are_not_deleted(step, group1, group2):
    results = recordings_dao.get_all()
    results_id = [item.cid for item in results]
    assert(group1 in results_id)
    assert(group2 in results_id)
