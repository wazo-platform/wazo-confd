Feature: REST API Link line with a user

    Scenario: Create an empty user_line
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        When I create an empty user_line
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: line_id"

    Scenario: Create a user_line with empty parameters
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        When I create the following user_line via RESTAPI:
            | user_id | line_id | main_user | main_line |
            | 1       |         |           |           |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: line_id must be integer,main_user must be boolean,main_line must be boolean"

    Scenario: Create a user_line with invalid values
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        When I create the following user_line via RESTAPI:
            | user_id | line_id | main_user | main_line |
            | 1       | toto    | ok        | non       |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: line_id must be integer,main_user must be boolean,main_line must be boolean"

    Scenario: Create a user_line with invalid parameters
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        When I create the following user_line via RESTAPI:
            | user_id | line_id | invalid |
            | 1       | 1       | invalid |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: invalid"

    Scenario: Create a user_line with a missing line id
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        When I create the following user_line via RESTAPI:
            | user_id | main_user |
            | 1       | True      |
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: line_id"

    Scenario: Create user_line with a line that doesn't exist
        Given I have no lines
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 1       | 10      |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: line_id 10 does not exist"

    Scenario: Create user_line with a user that doesn't exist
        Given I have no users
        Given I only have the following lines:
            | id | context | protocol | device_slot |
            | 10 | default | sip      | 1           |
        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 1       | 10      |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: user_id 1 does not exist"

    Scenario: Create a user_line
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        Given I only have the following lines:
            | id | context | protocol | device_slot |
            | 10 | default | sip      | 1           |
        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 1       | 10      |
        Then I get a response with status "201"
        Then I get a response with a link to the "lines" resource with id "10"
        Then I get a header with a location matching "/1.1/users/\d+/lines"

    Scenario: Associate 3 users to the same line
        Given I only have the following lines:
            | id | context | protocol | device_slot |
            | 10 | default | sip      | 1           |
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Salle     | Doctorant |
            | 2  | Greg      | Sanderson |
            | 3  | Roberto   | Da Silva  |
        When I create the following user_line via RESTAPI:
            | user_id | line_id | main_user |
            | 1       | 10      | True      |
        When I create the following user_line via RESTAPI:
            | user_id | line_id | main_user |
            | 2       | 10      | False     |
        When I create the following user_line via RESTAPI:
            | user_id | line_id | main_user |
            | 3       | 10      | False     |
        Then I get a response with status "201"

        Then I see a user with infos:
            | fullname        | protocol | context |
            | Salle Doctorant | sip      | default |
        Then I see a user with infos:
            | fullname       | protocol | context |
            | Greg Sanderson | sip      | default |
        Then I see a user with infos:
            | fullname         | protocol | context |
            | Roberto Da Silva | sip      | default |

    Scenario: Link a user already associated to a line
        Given I only have the following users:
            | id  | firstname | lastname  |
            | 1   | Greg      | Sanderson |
        Given I only have the following lines:
            | id | context     | protocol | device_slot |
            | 10 | default     | sip      | 1           |

        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 1       | 10      |
        Then I get a response with status "201"
        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 1       | 10      |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: user is already associated to this line"

    Scenario: Dissociate user_line with extension associated
        Given I only have the following users:
            | id  | firstname | lastname  |
            | 1   | Greg      | Sanderson |
        Given I only have the following extensions:
            | id | context | exten |
            | 5  | default |  1000 |
        Given I only have the following lines:
            | id | context     | protocol | username | secret | device_slot |
            | 10 | default     | sip      | toto     | tata   | 1           |

        When I create the following links:
            | user_id | line_id | extension_id |
            |  1      |  10     | 5            |
        Then I get a response with status "201"
        When I dissociate the following user_line via RESTAPI:
            | line_id | user_id |
            | 10      | 1       |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: There are an extension that already associated to this user_line"

    Scenario: Dissociate user_line that doesn't exist
        Given I have no user_line with the following parameters:
            | line_id | user_id |
            | 2       | 3       |
        When I dissociate the following user_line via RESTAPI:
            | line_id | user_id |
            | 2       | 3       |
        Then I get a response with status "404"
        Then I get an error message "UserLine with user_id=3, line_id=2 does not exist"

    Scenario: Dissociate user_line with main user
        Given I only have the following users:
            | id  | firstname | lastname  |
            | 1   | Greg      | Sanderson |
            | 2   | Cédric    | Abunar    |
        Given I only have the following lines:
            | id | context     | protocol | username | secret | device_slot |
            | 10 | default     | sip      | toto     | tata   | 1           |

        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 1       | 10      |
            | 2       | 10      |
        Then I get a response with status "201"

        When I dissociate the following user_line via RESTAPI:
            | line_id | user_id |
            | 10      | 1       |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: There are secondary users associated to this user_line"

    Scenario: Dissociate user_line with secondary user
        Given I only have the following users:
            | id  | firstname | lastname  |
            | 1   | Greg      | Sanderson |
            | 2   | Cédric    | Abunar    |
        Given I only have the following lines:
            | id | context     | protocol | username | secret | device_slot |
            | 10 | default     | sip      | toto     | tata   | 1           |

        When I create the following user_line via RESTAPI:
            | user_id | line_id |
            | 1       | 10      |
            | 2       | 10      |
        Then I get a response with status "201"

        When I dissociate the following user_line via RESTAPI:
            | user_id | line_id |
            | 2       | 10      |
        Then I get a response with status "204"
