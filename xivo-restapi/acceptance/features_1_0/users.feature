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
        Then I receive a response with status "404"

    Scenario: Creating a user
        Given there is no user "Irène" "Dupont"
        When I create a user "Irène Dupont" with description "accented description: éà@';" and with ctiprofileid "1"
        Then I receive a response with status "201"
        Then the user "Irène Dupont" is actually created with ctiprofileid "1" and description "accented description: éà@';"

    Scenario: Creation with errors
        When I create a user "Michel Sardou" with an field "unexisting_field" of value "value"
        Then I receive a response with status "400"
        Then I receive an error message "Incorrect parameters sent: unexisting_field"

    Scenario: Editing a user
        Given there is a user "Clémence Dupond"
        When I update the user "Clémence Dupond" with a last name "Brézé"
        Then I receive a response with status "200"
        Then I have a user "Clémence Brézé"

    Scenario: Editing a non existing user
        When I update a user with a non existing id with the last name "Dupond"
        Then I receive a response with status "404"

    Scenario: Editing with errors
        Given there is a user "Michel Sardou"
        When I update the user "Michel Sardou" with a field "unexisting_field" of value "value"
        Then I receive a response with status "400"
        Then I receive an error message "Incorrect parameters sent: unexisting_field"

    Scenario: Editing a user owning a voicemail
        Given there is a user "Clémence Dupond" with a voicemail
        When I update this user with a first name "Delphine" and a last name "Guébriant"
        Then I receive a response with status "200"
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
        Then I receive a response with status "200"
        Then this user no longer exists

    Scenario: Deleting a user member of a queue
        Given there is a queue named "myqueue"
        Given there is a user "Théodore Botrel" member of the queue "myqueue"
        When I delete this user
        Then this user no longer exists

    Scenario: Deleting a user with a rightcall
        Given there is a rightcall "my right call"
        Given there is a user "Théodore Botrel" with the right call "my right call"
        When I delete this user
        Then this user no longer exists

    Scenario: Deleting a user with a call filter
        Given there is a call filter "my call filter"
        Given there is a user "Théodore Botrel" with the call filter "my call filter"
        When I delete this user
        Then this user no longer exists

    Scenario: Deleting a user with a dialaction
        Given there is a user "Théodore Botrel" with a dialaction
        When I delete this user
        Then this user no longer exists

    Scenario: Deleting a user with a function key
        Given there is a user "Théodore Botrel" with a function key
        When I delete this user
        Then this user no longer exists

    Scenario: Deleting a user with a schedule
        Given there is a schedule "my schedule"
        Given there is a user "Théodore Botrel" with this schedule
        When I delete this user
        Then this user no longer exists

    Scenario: Deleting a non existing user
        When I delete a non existing user
        Then I receive a response with status "404"

    Scenario: Deletion refused if there is a voicemail
        Given there is a user "Alexandre Soljénitsyne" with a voicemail
        When I delete this user
        Then I receive a response with status "412"
        Then I receive an error message "Cannot remove a user with a voicemail. Delete the voicemail or dissociate it from the user."

    Scenario: Force voicemail deletion
        Given there is a user "Alexandre Soljénitsyne" with a voicemail
        When I delete this user and force voicemail deletion
        Then I receive a response with status "200"
        Then this user no longer exists
