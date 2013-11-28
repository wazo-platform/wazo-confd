Feature: REST API Link line with a user

    Scenario: Create an empty user_line
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 148384 | Greg      | Sanderson |
        When I create an empty user_line
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: line_id"

    Scenario: Create a user_line with invalid values
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 384939 | Greg      | Sanderson |
        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 384939  | toto    |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: line_id must be integer"

    Scenario: Create a user_line with invalid parameters
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 562668 | Greg      | Sanderson |
        When I create the following user_line via RESTAPI:
            | user_id | line_id | invalid |
            | 562668  | 999999  | invalid |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: invalid"

    Scenario: Create user_line with a line that doesn't exist
        Given I have no lines
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 495858 | Greg      | Sanderson |
        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 495858  | 682433  |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: line_id 682433 does not exist"

    Scenario: Create user_line with a user that doesn't exist
        Given I have no users
        Given I only have the following lines:
            | id     | context | protocol | device_slot |
            | 786225 | default | sip      | 1           |
        When I create the following user_line via RESTAPI:
            | line_id | user_id |
            | 786225  | 195322  |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: user_id 195322 does not exist"

    Scenario: Create a user_line
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 333222 | Greg      | Sanderson |
        Given I only have the following lines:
            | id     | context | protocol | device_slot |
            | 390845 | default | sip      | 1           |
        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 333222  | 390845  |
        Then I get a response with status "201"
        Then I get a response with a link to the "lines" resource with id "390845"
        Then I get a response with a link to the "users" resource with id "333222"
        Then I get a header with a location matching "/1.1/users/\d+/lines"

    Scenario: Associate 3 users to the same line
        Given I only have the following lines:
            | id     | context | protocol | device_slot |
            | 239487 | default | sip      | 1           |
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 983471 | Salle     | Doctorant |
            | 983472 | Greg      | Sanderson |
            | 983473 | Roberto   | Da Silva  |
        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 983471  | 239487  |
        Then I get a response with status "201"
        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 983472  | 239487  |
        Then I get a response with status "201"
        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 983473  | 239487  |
        Then I get a response with status "201"

        Then I see a user with infos:
            | fullname         | protocol | context |
            | Salle Doctorant  | sip      | default |
            | Greg Sanderson   | sip      | default |
            | Roberto Da Silva | sip      | default |

    Scenario: Link a user already associated to a line
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 980123 | Greg      | Sanderson |
        Given I only have the following lines:
            | id     | context | protocol | device_slot |
            | 948671 | default | sip      | 1           |

        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 980123  | 948671  |
        Then I get a response with status "201"
        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 980123  | 948671  |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: user is already associated to this line"

    Scenario: Get user_line when user does not exist
        Given there are no users with id "999999"
        When I request the lines associated to user id "999999" via RESTAPI
        Then I get a response with status "404"
        Then I get an error message "User with id=999999 does not exist"

    Scenario: Get user_line when line doesn't exist
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 594383 | Greg      | Sanderson |
        When I request the lines associated to user id "999999" via RESTAPI
        Then I get a response with status "404"
        Then I get an error message "User with id=999999 does not have any lines"

    Scenario: Get user_line
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 293847 | Greg      | Sanderson |
        Given I only have the following lines:
            | id     | context | protocol | username | secret | device_slot |
            | 943875 | default | sip      | toto     | tata   | 1           |
        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 293847  | 943875  |
        Then I get a response with status "201"

        When I request the lines associated to user id "293847"
        Then I get a response with status "200"
        Then I get a response with a user id
        Then I get a response with a line id
        Then I get a response with a link to the "lines_sip" resource using the id "line_id"
        Then I get a response with a link to the "users" resource using the id "user_id"

    Scenario: Dissociate user_line with extension associated
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 594831 | Greg      | Sanderson |
        Given I only have the following extensions:
            | id     | context | exten |
            | 493820 | default | 1435  |
        Given I only have the following lines:
            | id     | context | protocol | username | secret | device_slot |
            | 493837 | default | sip      | toto     | tata   | 1           |

        When I create the following links:
            | user_id | line_id | extension_id |
            | 594831  | 493837  | 493820       |
        Then I get a response with status "201"
        When I dissociate the following user_line via RESTAPI:
            | line_id | user_id |
            | 493837  | 594831  |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: There is an extension associated to this line"

    Scenario: Dissociate user_line that doesn't exist
        Given I have no user_line with the following parameters:
            | line_id | user_id |
            | 888252  | 777252  |
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 777252 | Greg      | Sanderson |
        When I dissociate the following user_line via RESTAPI:
            | line_id | user_id |
            | 888252  | 777252  |
        Then I get a response with status "404"
        Then I get an error message "User with id=777252 does not have any line"

    Scenario: Dissociate user_line with main user
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 437501 | Greg      | Sanderson |
            | 304832 | Cédric    | Abunar    |
        Given I only have the following lines:
            | id     | context | protocol | username | secret | device_slot |
            | 594399 | default | sip      | toto     | tata   | 1           |

        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 437501  | 594399  |
            | 304832  | 594399  |
        Then I get a response with status "201"

        When I dissociate the following user_line via RESTAPI:
            | line_id | user_id |
            | 594399  | 437501  |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: There are secondary users associated to this line"

    Scenario: Dissociate user_line with secondary user
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 693755 | Greg      | Sanderson |
            | 593820 | Cédric    | Abunar    |
        Given I only have the following lines:
            | id     | context | protocol | username | secret | device_slot |
            | 150349 | default | sip      | toto     | tata   | 1           |

        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 693755  | 150349  |
            | 593820  | 150349  |
        Then I get a response with status "201"

        When I dissociate the following user_line via RESTAPI:
            | user_id | line_id |
            | 593820  | 150349  |
        Then I get a response with status "204"
