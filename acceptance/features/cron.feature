Feature: Automatic deletion - must be launched as super user

	In order to avoid hard disk overloading
	
	Scenario: WAV files deletion
	  Given there is a directory "/var/lib/pf-xivo/sounds/campagnes"
	  Given there is a file "test1.wav" created "40" days ago
	  Given there is a file "test2.wav" created "32" days ago
	  Given there is a file "test3.wav" created "31" days ago
	  Given there is a file "test4.wav" created today
	  When I run the script "../cron_job/delete_old_items"
	  Then "test1.wav" and "test2.wav" are deleted
	  Then "test3.wav" and "test4.wav" are not deleted
	  
	Scenario: Database items deletion
	  Given there is no campaign
	  Given there is a campaign of id "1"
	  Given there is an agent of number "222"
	  Given there is a recording with id "test1" created "40" days ago with campaign "1" and agent "222"
	  Given there is a recording with id "test2" created "31" days ago with campaign "1" and agent "222"
	  Given there is a recording with id "test3" created "15" days ago with campaign "1" and agent "222"
	  Given there is a recording with id "test4" created "0" days ago with campaign "1" and agent "222"
	  When I run the script "../cron_job/delete_old_items"
	  Then items "test1" and "test2" are deleted
	  Then items "test3" and "test4" are not deleted
	  