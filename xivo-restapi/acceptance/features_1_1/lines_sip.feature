Feature: SIP Lines

    Scenario: Create an empty SIP line
        When I create an empty SIP line
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: context"

    Scenario: Create a line with an empty context
        When I create a line_sip with the following parameters:
            | context |
            |         |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: context cannot be empty"

    Scenario: Create a line with a context that doesn't exist
        When I create a line_sip with the following parameters:
            | context           |
            | superdupercontext |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: context superdupercontext does not exist"

    Scenario: Create a line with invalid parameters
        When I create a line_sip with the following parameters:
            | context | invalidparameter |
            | default | invalidvalue     |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: invalidparameter"

    Scenario: Create a line with a context
        When I create a line_sip with the following parameters:
            | context |
            | default |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a response with a link to the "lines_sip" resource
        Then I get a header with a location for the "lines_sip" resource

    Scenario: Create a line with an internal context other than default
        Given I have an internal context named "mycontext"
        When I create a line_sip with the following parameters:
            | context     |
            | mycontext   |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a response with a link to the "lines_sip" resource
        Then I get a header with a location for the "lines_sip" resource

    Scenario: Create 2 lines in same context
        When I create a line_sip with the following parameters:
            | context |
            | default |
        Then I get a response with status "201"
        When I create a line_sip with the following parameters:
            | context |
            | default |
        Then I get a response with status "201"

    Scenario: Editing a line_sip that doesn't exist
        Given I have no lines
        When I update the line_sip with id "1" using the following parameters:
          | username |
          | toto     |
        Then I get a response with status "404"

    Scenario: Editing a line_sip with parameters that don't exist
        Given I only have the following lines:
          | id | username | context |
          | 1  | toto     | default |
        When I update the line_sip with id "1" using the following parameters:
          | unexisting_field |
          | unexisting value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Editing the username of a line_sip
        Given I only have the following lines:
          | id | username | context |
          | 1  | toto     | default |
        When I update the line_sip with id "1" using the following parameters:
          | username |
          | tata  |
        Then I get a response with status "204"
        When I ask for the line_sip with id "1"
        Then I have a line_sip with the following parameters:
          | id | username | context |
          | 1  | tata     | default |

    Scenario: Editing the context of a line_sip
        Given I only have the following lines:
          | id | username | context |
          | 1  | toto     | default |
        Given I have the following context:
          | name | numberbeg | numberend |
          | lolo | 1000      | 1999      |
        When I update the line_sip with id "1" using the following parameters:
          | context |
          | lolo    |
        Then I get a response with status "204"
        When I ask for the line_sip with id "1"
        Then I have a line_sip with the following parameters:
          | id | username | context |
          | 1  | toto     | lolo    |

    Scenario: Editing the callerid of a line
        Given I only have the following lines:
          | id | username | context | callerid   |
          | 1  | toto     | default | Super Toto |
        Given I have the following context:
          | name | numberbeg | numberend |
          | lolo | 1000      | 1999      |
        When I update the line_sip with id "1" using the following parameters:
          | callerid  |
          | Mega Toto |
        Then I get a response with status "204"
        When I ask for the line_sip with id "1"
        Then I have a line_sip with the following parameters:
          | id | username | context | callerid  |
          | 1  | toto     | lolo    | Mega Toto |

    Scenario: Editing the username, context, callerid of a line_sip
        Given I only have the following lines:
          | id | username | context | callerid   |
          | 1  | titi     | default | Super Toto |
        Given I have the following context:
          | name   | numberbeg | numberend |
          | patate | 1000      | 1999      |
        When I update the line_sip with id "1" using the following parameters:
          | username | context | callerid   |
          | titi     | patate  | Petit Toto |
        Then I get a response with status "204"
        When I ask for the line_sip with id "1"
        Then I have a line_sip with the following parameters:
          | id | username | context | callerid   |
          | 1  | titi     | patate  | Petit Toto |
          
    Scenario: Delete a line that doesn't exist
        Given I have no lines
        When I delete line sip "10"
        Then I get a response with status "404"

    Scenario: Delete a line
        Given I only have the following lines:
            | id | context | protocol |
            | 10 | default | sip      |
        When I delete line sip "10"
        Then I get a response with status "204"
        Then the line sip "10" no longer exists
        Then the line "10" no longer exists
