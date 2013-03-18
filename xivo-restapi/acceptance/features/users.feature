Feature: Users management

	Scenario: Users listing
	  Given there is no user
	  Given there is a user "Clémence Dupond"
	  Given there is a user "Louis Martin"
	  When I ask for all the users
	  Then I get a list with "Clémence Dupond" and "Louis Martin"
	  
	Scenario: Getting an existing user
	  Given there is no user
	  Given there is a user "Clémence Dupond"
	  When I ask for the user "Clémence Dupond" using its id
	  Then I get a single user "Clémence Dupond"
	  
	Scenario: Getting a non existing user
	  Given there is no user
	  When I ask for the user of id "1"
	  Then I get a response with status "404"
	  
	Scenario: Creating a user
	  Given there is no user
	  When I create a user "Clémence Dupond" with description "accented description: éà@';" and with ctiprofileid "1"
	  Then I get a response with status "201"
	  Then the user "Clémence Dupond" is actually created with ctiprofileid "1" and description "accented description: éà@';"
	  
	Scenario: Creation with errors
	  Given there is no user
	  When I create a user "Michel Sardou" with an field "unexisting_field" of value "value"
	  Then I get a response with status "400"
	  Then I get an error message "Incorrect parameters sent: unexisting_field"
	  
	Scenario: Editing a user
	  Given there is no user
	  Given there is a user "Clémence Dupond"
	  When I update the user "Clémence Dupond" with a last name "Brézé"
	  Then I get a response with status "200"
	  Then I have a user "Clémence Brézé"
	  
	Scenario: Editing a non existing user
	  Given there is no user
	  When I update the user of id "1" with the last name "Dupond"
	  Then I get a response with status "404"
	  
	Scenario: Edition with errors
	  Given there is no user
	  Given there is a user "Michel Sardou"
	  When I update the user "Michel Sardou" with a field "unexisting_field" of value "value"
	  Then I get a response with status "400"
	  Then I get an error message "Incorrect parameters sent: unexisting_field"
