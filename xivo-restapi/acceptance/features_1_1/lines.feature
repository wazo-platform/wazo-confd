Feature: Lines

    Scenario: Line list with no lines
        Given I have no lines
        When I ask for the list of lines
        Then I get an empty list

    Scenario: Delete a line that doesn't exist
        Given I have no lines
        When I delete line "10"
        Then I get a response with status "404"

    Scenario: Delete a line
        Given I only have the following lines:
            | id | context | protocol |
            | 10 | default | sip      |

        When I delete line "10"
        Then I get a response with status "204"
        Then the line "10" no longer exists