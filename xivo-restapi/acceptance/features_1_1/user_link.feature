Feature: Link user with a line and extension

    Scenario: Create an empty link
        When I create an empty link
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: user_id,line_id,extension_id"

    Scenario: Create a link with empty parameters
        When I create a link with the following parameters:
            | user_id | extension_id | line_id |
            |         |              |         |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: user_id must be integer,line_id must be integer,extension_id must be integer"

    Scenario: Create a link with invalid values
        When I create a link with the following invalid parameters:
            | user_id | extension_id | line_id |
            | asdf    | 1            | 2       |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: user_id must be integer,line_id must be integer,extension_id must be integer"

    Scenario: Create a link with invalid parameters
        When I create a link with the following parameters:
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

    Scenario: Create link with an extension that doesn't exist
        Given there are no extensions
        Given I have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        Given I have the following lines:
            | id | context | protocol |
            | 10 | default | sip      |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: extension_id"

    Scenario: Create link with a line that doesn't exist
        Given there are no lines
        Given I have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        Given I have the following extensions:
            | id  | context | exten | type | typeval |
            | 100 | default | 1000  | user | 1       |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: line_id"

    Scenario: Create link with a user that doesn't exist
        Given there are no users
        Given I have the following lines:
            | id | context | protocol |
            | 10 | default | sip      |
        Given I have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: user_id"

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

        Then I get a response with a link to the "user_link" resource
        Then I get a response with a link to the "extension" resource
        Then I get a response with a link to the "line" resource
        Then I get a response with a link to the "user" resource
        Then I get a header with a location for the "user_link" resource
        #Then I see the line with an extension in the webi
        #Then I see a user with a line in the webi
        #Then I can pass a call with a SIP phone

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

        Then I get a response with a link to the "user_link" resource
        Then I get a response with a link to the "extension" resource
        Then I get a response with a link to the "line" resource
        Then I get a response with a link to the "user" resource
        Then I get a header with a location for the "user_link" resource

        #Then I see the line with an extension in the webi
        #Then I see a user with a line in the webi
        #Then I see the extension in the "statscenter" dialplan
