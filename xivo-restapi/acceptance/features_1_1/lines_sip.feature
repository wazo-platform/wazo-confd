Feature: SIP Lines

    Scenario: Create an empty SIP line
        When I create an empty SIP line
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: context,device_slot"

    Scenario: Create a line with an empty context
        When I create a line_sip with the following parameters:
            | context | device_slot |
            |         | 1           |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: context cannot be empty"

    Scenario: Create a line with an empty device_slot
        When I create a line_sip with the following parameters:
            | context | device_slot |
            | default |             |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: device_slot must be numeric"

    Scenario: Create a line with an invalid device_slot
        When I create a line_sip with the following parameters:
            | context | device_slot |
            | default | toto        |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: device_slot must be numeric"
        When I create a line_sip with the following parameters:
            | context | device_slot |
            | default | 0           |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: device_slot must be greater than 0"
        When I create a line_sip with the following parameters:
            | context | device_slot |
            | default | -1          |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: device_slot must be greater than 0"

    Scenario: Create a line with a context that doesn't exist
        When I create a line_sip with the following parameters:
            | context           | device_slot |
            | superdupercontext | 1           |
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
            | context | device_slot |
            | default | 1           |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a response with a link to the "lines_sip" resource
        Then I get a header with a location for the "lines_sip" resource

    Scenario: Create a line with an internal context other than default
        Given I have an internal context named "mycontext"
        When I create a line_sip with the following parameters:
            | context     | device_slot |
            | mycontext   | 1           |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a response with a link to the "lines_sip" resource
        Then I get a header with a location for the "lines_sip" resource

    Scenario: Create 2 lines in same context
        When I create a line_sip with the following parameters:
            | context | device_slot |
            | default | 1           |
        Then I get a response with status "201"
        When I create a line_sip with the following parameters:
            | context | device_slot |
            | default | 1           |
        Then I get a response with status "201"

    Scenario: Editing a line_sip that doesn't exist
        Given I have no lines
        When I update the line_sip with id "10" using the following parameters:
          | username |
          | toto     |
        Then I get a response with status "404"

    Scenario: Editing a line_sip with parameters that don't exist
        Given I only have the following lines:
          | id | username | context | protocol | device_slot |
          | 10 | toto     | default | sip      | 1           |
        When I update the line_sip with id "10" using the following parameters:
          | unexisting_field |
          | unexisting value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Editing the username of a line_sip
        Given I only have the following lines:
          | id | username | context | protocol | device_slot |
          | 10 | toto     | default | sip      | 1           |
        When I update the line_sip with id "10" using the following parameters:
          | username |
          | tata     |
        Then I get a response with status "204"
        When I ask for the line_sip with id "10"
        Then I have a line_sip with the following parameters:
          | id | username | context |
          | 10 | tata     | default |

    Scenario: Editing the context of a line_sip
        Given I only have the following lines:
            | id | username | context | protocol | device_slot |
            | 10 | toto     | default | sip      | 1           |
        Given I have the following context:
            | name | numberbeg | numberend |
            | lolo | 1000      | 1999      |
        When I update the line_sip with id "10" using the following parameters:
            | context |
            | lolo    |
        Then I get a response with status "204"
        When I ask for the line_sip with id "10"
        Then I have a line_sip with the following parameters:
            | id | username | context |
            | 10 | toto     | lolo    |

    Scenario: Editing a line_sip with a context that doesn't exist
        Given I only have the following lines:
          | id | username | context | protocol | device_slot |
          | 10 | toto     | default | sip      | 1           |
        Given I have the following context:
          | name | numberbeg | numberend |
          | lolo | 1000      | 1999      |
        When I update the line_sip with id "10" using the following parameters:
          | context             |
          | mysuperdupercontext |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: context mysuperdupercontext does not exist"

    Scenario: Editing the callerid of a line
        Given I only have the following lines:
          | id | username | context | callerid   | protocol | device_slot |
          | 10 | toto     | default | Super Toto | sip      | 1           |
        Given I have the following context:
          | name | numberbeg | numberend |
          | lolo | 1000      | 1999      |
        When I update the line_sip with id "10" using the following parameters:
          | callerid  |
          | Mega Toto |
        Then I get a response with status "204"
        When I ask for the line_sip with id "10"
        Then I have a line_sip with the following parameters:
          | id | username | context | callerid  |
          | 10 | toto     | default | Mega Toto |

    Scenario: Editing the username, context, callerid of a line_sip
        Given I only have the following lines:
          | id | username | context | callerid   | protocol | device_slot |
          | 10 | titi     | default | Super Toto | sip      | 1           |
        Given I have the following context:
          | name   | numberbeg | numberend |
          | patate | 1000      | 1999      |
        When I update the line_sip with id "10" using the following parameters:
          | username | context | callerid   |
          | titi     | patate  | Petit Toto |
        Then I get a response with status "204"
        When I ask for the line_sip with id "10"
        Then I have a line_sip with the following parameters:
          | id | username | context | callerid   |
          | 10 | titi     | patate  | Petit Toto |
          
    Scenario: Delete a line that doesn't exist
        Given I have no lines
        When I delete line sip "10"
        Then I get a response with status "404"

    Scenario: Delete a line
        Given I only have the following lines:
            | id | context | protocol | device_slot |
            | 10 | default | sip      | 1           |
        When I delete line sip "10"
        Then I get a response with status "204"
        Then the line sip "10" no longer exists
        Then the line "10" no longer exists
