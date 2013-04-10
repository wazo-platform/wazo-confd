Feature: Users management

	Scenario: Users listing
	  Given there is a user "Clémence Dupond"
	  Given there is a user "Louis Martin"
	  When I ask for all the users
	  Then I get a list with "Clémence Dupond" and "Louis Martin"
	  
	Scenario: Getting an existing user
	  Given there is a user "Clémence Dupond"
	  When I ask for the user "Clémence Dupond" using its id
	  Then I get a single user "Clémence Dupond"
	  
	Scenario: Getting a non existing user
	  When I ask for a user with a non existing id
	  Then I get a response with status "404"
	  
	Scenario: Creating a user
	  When I create a user "Irène Dupont" with description "accented description: éà@';" and with ctiprofileid "1"
	  Then I get a response with status "201"
	  Then the user "Irène Dupont" is actually created with ctiprofileid "1" and description "accented description: éà@';"
	  Then I delete the user "Irène Dupont" from the database
	  
	Scenario: Creation with errors
	  When I create a user "Michel Sardou" with an field "unexisting_field" of value "value"
	  Then I get a response with status "400"
	  Then I get an error message "Incorrect parameters sent: unexisting_field"
	  
	Scenario: Editing a user
	  Given there is a user "Clémence Dupond"
	  When I update the user "Clémence Dupond" with a last name "Brézé"
	  Then I get a response with status "200"
	  Then I have a user "Clémence Brézé"
	  
	Scenario: Editing a non existing user
	  When I update a user with a non existing id with the last name "Dupond"
	  Then I get a response with status "404"
	  
	Scenario: Edition with errors
	  Given there is a user "Michel Sardou"
	  When I update the user "Michel Sardou" with a field "unexisting_field" of value "value"
	  Then I get a response with status "400"
	  Then I get an error message "Incorrect parameters sent: unexisting_field"
	
	Scenario: Editing a user owning a voicemail
	  Given there is a user "Clémence Dupond" with a voicemail
	  When I update this user with a first name "Delphine" and a last name "Guébriant"
	  Then I get a response with status "200"
	  Then this user has a voicemail "Delphine Guébriant"

	Scenario: Line property
	  Given there is a user "André Charrier" with a line "44500"
  	  When I ask for the user "André Charrier" using its id
	  Then I have a single user "André Charrier" with a line "44500"
	  When I ask for all the users
	  Then I have a user "André Charrier" with a line "44500"
	  Then I delete this line

	Scenario: User deletion with a SIP line
	  Given there is a user "André Charrier" with a SIP line "2000"
	  When I delete this user
	  Then I get a response with status "200"
	  Then no data is remaining in the tables "userfeatures,linefeatures,usersip,extensions,extenumbers,contextnummember"

	#TODO: manual step
	#Given I have a device with no line
	#Given I have a user with a SIP line associated to this device
	#When I delete this user
	#Then The device is reset to autoprov mode