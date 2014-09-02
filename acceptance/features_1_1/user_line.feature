Feature: REST API Link line with a user

    Scenario: Create a user_line
        Given I have the following users:
            | id     | firstname | lastname  |
            | 333222 | Greg      | Sanderson |
        Given I have the following lines:
            | id     | context | protocol | device_slot |
            | 390845 | default | sip      | 1           |
        When I create the following user_line via CONFD:
            | user_id | line_id |
            | 333222  | 390845  |
        Then I get a response with status "201"
        Then I get a response with a link to the "lines" resource with id "390845"
        Then I get a response with a link to the "users" resource with id "333222"
        Then I get a header with a location matching "/1.1/users/\d+/lines"

    Scenario: Create a user_line with a line that has an extension
        Given I have the following users:
            | id     | firstname | lastname  |
            | 597172 | Greg      | Sanderson |
        Given I have the following lines:
            | id     | context | protocol | device_slot |
            | 879216 | default | sip      | 1           |
        Given I have the following extensions:
            | id     | exten | context |
            | 146633 | 1983  | default |
        Given line "879216" is linked with extension "1983@default"
        When I create the following user_line via CONFD:
            | user_id | line_id |
            | 597172  | 879216  |
        Then I get a response with status "201"
        Then I get a response with a link to the "lines" resource with id "879216"
        Then I get a response with a link to the "users" resource with id "597172"
        Then I get a header with a location matching "/1.1/users/\d+/lines"

    Scenario: Associate 3 users to the same line
        Given I have the following lines:
            | id     | context | protocol | device_slot |
            | 239487 | default | sip      | 1           |
        Given I have the following users:
            | id     | firstname | lastname  |
            | 983471 | Salle     | Doctorant |
            | 983472 | Greg      | Sanderson |
            | 983473 | Roberto   | Da Silva  |
        When I create the following user_line via CONFD:
            | user_id | line_id |
            | 983471  | 239487  |
        Then I get a response with status "201"
        When I create the following user_line via CONFD:
            | user_id | line_id |
            | 983472  | 239487  |
        Then I get a response with status "201"
        When I create the following user_line via CONFD:
            | user_id | line_id |
            | 983473  | 239487  |
        Then I get a response with status "201"
        Then I see a user with infos:
            | fullname         | protocol |
            | Salle Doctorant  | sip      |
            | Greg Sanderson   | sip      |
            | Roberto Da Silva | sip      |

    Scenario: Get user_line associations when there are no lines associated to a user
        Given I have the following users:
            | id     | firstname | lastname  |
            | 594383 | Greg      | Sanderson |
        When I request the lines associated to user id "594383" via CONFD
        Then I get a response with status "200"
        Then I get an empty list

    Scenario: Get user_line
        Given I have the following users:
            | id     | firstname | lastname  |
            | 293847 | Greg      | Sanderson |
        Given I have the following lines:
            | id     | context | protocol | username | secret | device_slot |
            | 943875 | default | sip      | toto     | tata   | 1           |
        Given line "943875" is linked with user id "293847"
        When I request the lines associated to user id "293847" via CONFD
        Then I get a response with status "200"
        Then each item has a "users" link using the id "user_id"
        Then each item has a "lines" link using the id "line_id"

    Scenario: Dissociate user_line with extension associated
        Given I have the following users:
            | id     | firstname | lastname  |
            | 594831 | Greg      | Sanderson |
        Given I have the following lines:
            | id     | context | protocol | username | secret | device_slot |
            | 493837 | default | sip      | toto     | tata   | 1           |
        Given I have the following extensions:
            | id     | context | exten |
            | 493820 | default | 1435  |
        Given line "493837" is linked with user id "594831"
        Given line "493837" is linked with extension "1435@default"
        When I dissociate the following user_line via CONFD:
            | line_id | user_id |
            | 493837  | 594831  |
        Then I get a response with status "204"

    Scenario: Dissociate user_line with secondary user
        Given I have the following users:
            | id     | firstname | lastname  |
            | 693755 | Greg      | Sanderson |
            | 593820 | Cédric    | Abunar    |
        Given I have the following lines:
            | id     | context | protocol | username | secret | device_slot |
            | 150349 | default | sip      | toto     | tata   | 1           |
        Given line "150349" is linked with user id "693755"
        Given line "150349" is linked with user id "593820"
        When I dissociate the following user_line via CONFD:
            | user_id | line_id |
            | 593820  | 150349  |
        Then I get a response with status "204"
        When I dissociate the following user_line via CONFD:
            | user_id | line_id |
            | 693755  | 150349  |
        Then I get a response with status "204"

    Scenario: Dissociate user_line when a device is associated
        Given I have the following users:
            | id     | firstname | lastname    |
            | 477024 | Roger     | Brainsville |
        Given I have the following devices:
          | id                               | ip             | mac               |
          | 778bb97fee77f390583c463655128033 | 192.168.168.55 | 03:3f:44:aa:4a:2b |
        Given I have the following lines:
            | id     | context | protocol | username | secret   | device_slot | device_id                        |
            | 889863 | default | sip      | a8b7d45r | 8d8gjh53 | 1           | 778bb97fee77f390583c463655128033 |
        Given line "889863" is linked with user id "477024"
        When I dissociate the following user_line via CONFD:
            | line_id | user_id |
            | 889863  | 477024  |
        Then I get a response with status "400"
        Then I get an error message matching "Resource Error - Line is associated with a Device"
