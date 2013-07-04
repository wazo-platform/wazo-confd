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
        Given there is no user "Irène Dupont"
        When I create a user "Irène Dupont" with description "accented description: éà@';"
        Then I get a response with status "201"
        Then the user "Irène Dupont" is actually created with description "accented description: éà@';"

    Scenario: Creating a user with unexisting field
        Given there is no user "Michel Sardou"
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

    Scenario: Editing a user with unexisting field
        Given there is a user "Michel Sardou"
        When I update the user "Michel Sardou" with a field "unexisting_field" of value "value"
        Then I get a response with status "400"
        Then I get an error message "Incorrect parameters sent: unexisting_field"

    Scenario: Editing a user owning a voicemail
        Given there is no user "Clémence Dupond"
        Given there is no user "Delphine Guébriant"
        Given there is a user "Clémence Dupond" with a voicemail
        When I update this user with a first name "Delphine" and a last name "Guébriant"
        Then I get a response with status "200"
        Then this user has a voicemail "Delphine Guébriant"

    Scenario: Deleting a user 
        Given there is a user "Théodore Botrel"
        When I delete this user
        Then this user no longer exists

    Scenario: Deleting a non existing user
        When I delete a non existing user
        Then I get a response with status "404"
