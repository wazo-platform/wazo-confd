Feature: Link user with a line and extension

    Scenario: Create an empty link
        When I create an empty link
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: user_id,line_id,extension_id"

    Scenario: Create a link with empty parameters
        When I create a link with the following invalid parameters:
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
        Given I have no extensions
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        Given I only have the following lines:
            | id | context | protocol |
            | 10 | default | sip      |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: extension_id 100 does not exist"

    Scenario: Create link with a line that doesn't exist
        Given I have no lines
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        Given I only have the following extensions:
            | id  | context | exten | type | typeval |
            | 100 | default | 1000  | user | 1       |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: line_id 10 does not exist"

    Scenario: Create link with a user that doesn't exist
        Given I have no users
        Given I only have the following lines:
            | id | context | protocol |
            | 10 | default | sip      |
        Given I only have the following extensions:
            | id  | context | exten | type | typeval |
            | 100 | default | 1000  | user | 1       |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: user_id 1 does not exist"

    Scenario: Create a link
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        Given I only have the following lines:
            | id | context | protocol |
            | 10 | default | sip      |
        Given I only have the following extensions:
            | id  | context | exten | type | typeval |
            | 100 | default | 1000  | user | 1       |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "201"

        Then I get a response with a link to the "user_links" resource
        Then I get a response with a link to the "extensions" resource with id "100"
        Then I get a response with a link to the "lines" resource with id "10"
        Then I get a response with a link to the "users" resource with id "1"
        Then I get a header with a location for the "user_links" resource

    Scenario: Create a link in another context
        Given I have an internal context named "mycontext"
        Given I only have the following users:
            | id  | firstname | lastname  |
            | 1   | Greg      | Sanderson |
        Given I only have the following lines:
            | id  | context   | protocol  |
            | 10  | mycontext | sip       |
        Given I only have the following extensions:
            | id  | context   | exten     | type | typeval |
            | 100 | mycontext | 1000      | user | 1       |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "201"
        Then I get a response with a link to the "user_links" resource
        Then I get a response with a link to the "extensions" resource with id "100"
        Then I get a response with a link to the "lines" resource with id "10"
        Then I get a response with a link to the "users" resource with id "1"
        Then I get a header with a location for the "user_links" resource

    Scenario: Create a link with a provision device
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        Given I only have the following lines:
            | id | context | protocol | username | secret | num |
            | 10 | default | sip      | toto     | tata   | 1   |
        Given I only have the following extensions:
            | id  | context | exten | type | typeval |
            | 100 | default | 1000  | user | 1       |
        Given I only have the following devices:
            | id | ip       | mac               |
            | 20 | 10.0.0.1 | 00:00:00:00:00:00 |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "201"

        Then I get a response with a link to the "user_links" resource
        Then I get a response with a link to the "extensions" resource with id "100"
        Then I get a response with a link to the "lines" resource with id "10"
        Then I get a response with a link to the "users" resource with id "1"
        Then I get a header with a location for the "user_links" resource
        
        When I provision my device with my line_id "10" and ip "10.0.0.1"
        Then the device "20" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | toto     | toto          | tata     |
        
