Feature: Lines

    Scenario: Line list with no lines
        Given I have no lines
        When I ask for the list of lines
        Then I get an empty list

    Scenario: User link list by line_id no line
        Given I have no lines
        When I ask for the list of user_links with line_id "10"
        Then I get a response with status "200"
        Then I get an empty list

    Scenario: User link list by line_id with 1 user
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        Given I only have the following lines:
            | id | context | protocol | device_slot |
            | 10 | default | sip      | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        Given the following users, lines, extensions are linked:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        When I ask for the list of user_links with line_id "10"
        Then I get a response with status "200"
        Then I get the user_links with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |

    Scenario: User link list by line_id with 2 users
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
            | 2  | Cedric    | Abunar    |
        Given I only have the following lines:
            | id | context | protocol | device_slot |
            | 10 | default | sip      | 1           |
            | 20 | default | sip      | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        Given the following users, lines, extensions are linked:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
            | 2       | 10      | 100          |
        When I ask for the list of user_links with line_id "10"
        Then I get a response with status "200"
        Then I get the user_links with the following parameters:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
            | 2       | 10      | 100          |
