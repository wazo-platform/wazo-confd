Feature: Link user with a line and extension

    Scenario: Create an empty link
        When I create an empty link
        Then I get a response with status "400"
        #WARN: only one parameter appears in the error message
        Then I get an error message "Missing parameters: user_id,extension_id,line_id"

    FAIL
    Scenario: Create a link with empty parameters
        When I create a link with the following parameters:
            | user_id | extension_id | line_id |
            |         |              |         |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: user_id,extension_id,line_id"

    FAIL
    Scenario: Create a link with invalid values
        When I create a link with the following parameters:
            | user_id | extension_id | line_id |
            | asdf    | 1            | 2       |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: user_id"

    FAIL
    Scenario: Create a line with invalid parameters
        When I create a line with the following properties:
            | user_id | extension_id | line_id | invalid |
            | 3       | 1            | 2       | invalid |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: invalid"

    Scenario: Create a link with a missing line id
        When I create a link with the following parameters:
            | user_id | extension_id |
            | 1       | 2            |
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: line_id"

    FAIL
    Scenario: Create link with an extension that doesn't exist
        Given I have the following users:
            | id | firstname |
            | 1  | Greg      |
        Given I have the following lines:
            | id | context |
            | 10 | default |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        #WARN: returns 404 instead of 400
        Then I get a response with status "400"
        #WARN: no error message
        Then I get an error message "Invalid parameters: extension_id"

    FAIL
    Scenario: Create link with a line that doesn't exist
        Given I have the following users:
            | id | firstname |
            | 1  | Greg      |
        Given I have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        #WARN: returns 404 instead of 400
        Then I get a response with status "400"
        #WARN: no error message
        Then I get an error message "Invalid parameters: line_id"

    FAIL
    Scenario: Create link with a user that doesn't exist
        Given I have the following lines:
            | id | context |
            | 10 | default |
        Given I have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        #WARN: returns 404 instead of 400
        Then I get a response with status "400"
        #WARN: no error message
        Then I get an error message "Invalid parameters: user_id"

    FAIL
    Scenario: Create a link
        Given I have the following users:
            | id | firstname |
            | 1  | Greg      |
        Given I have the following lines:
            | id | context |
            | 10 | default |
        Given I have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "201"
        Then I get a link with an id

        Then I get a link to an extension
        Then I get a link to a line
        Then I get a link to a user
        Then I get a link to a user_link

        Then I get a location in the headers
        Then I see the line with an extension in the webi
        Then I see a user with a line in the webi
        Then I can pass a call with a SIP phone

    FAIL
    Scenario: Create a link in another context
        Given I have the following users:
            | id | firstname |
            | 1  | Greg      |
        Given I have the following lines:
            | id | context     |
            | 10 | statscenter |
        Given I have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "201"

        Then I see the line with an extension in the webi
        Then I see a user with a line in the webi
        Then I see the extension in the "statscenter" dialplan
