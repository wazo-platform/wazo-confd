Feature: Automatic deletion - must be launched as super user

	In order to avoid hard disk overlaoding
	
	Scenario: WAV files deletion
	  Given there is a directory "/var/lib/pf-xivo/sounds/campagnes"
	  Given there is a file "test1" created "40" days ago
	  Given there is a file "test2" created "31" days ago
	  Given there is a file "test3" created "15" days ago
	  Given there is a file "test4" created today
	  When I run the script "../cron_job/delete_old_items"
	  Then "test1" and "test2" are deleted
	  Then "test3" and "test4" are not deleted