Feature: REST API Lines

    Scenario: List lines
        Given I have the following lines:
            | id     | context | protocol | device_slot |
            | 387574 | default | sip      | 1           |
        When I ask for the list of lines
        Then I get a response with status "200"
        Then I get a list containing the following lines:
            | id     | context | protocol | device_slot |
            | 387574 | default | sip      | 1           |

    Scenario: Get a line
        Given I have the following lines:
            | id     | context | protocol | device_slot |
            | 751225 | default | sip      | 1           |
        When I ask for line with id "751225"
        Then I get a response with status "200"
        Then I get a line with the following parameters:
            | id     | context | protocol | device_slot |
            | 751225 | default | sip      | 1           |
