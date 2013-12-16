Feature: REST API Lines

    Scenario: User link list by line_id no line
        Given I have no line with id "964135"
        When I ask for the list of user_links with line_id "964135"
        Then I get a response with status "200"
        Then I get an empty list

    Scenario: User link list by line_id with 1 user
        Given I have the following users:
            |     id | firstname | lastname  |
            | 545325 | Greg      | Sanderson |
        Given I have the following lines:
            |     id | context | protocol | device_slot |
            | 332494 | default | sip      |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 133549 | default |  1000 |
        Given the following users, lines, extensions are linked:
            | user_id | line_id | extension_id |
            |  545325 |  332494 |       133549 |
        When I ask for the list of user_links with line_id "332494"
        Then I get a response with status "200"
        Then I get the user_links with the following parameters:
            | user_id | line_id | extension_id |
            |  545325 |  332494 |       133549 |

    Scenario: User link list by line_id with 2 users
        Given I have the following users:
            |     id | firstname | lastname  |
            | 565413 | Greg      | Sanderson |
            | 132498 | Cedric    | Abunar    |
        Given I have the following lines:
            |     id | context | protocol | device_slot |
            | 621654 | default | sip      |           1 |
            | 132497 | default | sip      |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 232321 | default |  1000 |
        Given the following users, lines, extensions are linked:
            | user_id | line_id | extension_id |
            |  565413 |  621654 |       232321 |
            |  132498 |  621654 |       232321 |
        When I ask for the list of user_links with line_id "621654"
        Then I get a response with status "200"
        Then I get the user_links with the following parameters:
            | user_id | line_id | extension_id |
            |  565413 |  621654 |       232321 |
            |  132498 |  621654 |       232321 |
