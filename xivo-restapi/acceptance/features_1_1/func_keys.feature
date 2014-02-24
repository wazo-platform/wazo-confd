Feature: REST API Function keys

    Scenario: List of function keys with invalid parameters
        When I request the list of func keys with the following parameters via RESTAPI:
            | limit |
            | -32   |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: limit must be a positive integer"

        When I request the list of func keys with the following parameters via RESTAPI:
            | limit |
            | asdf  |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: limit must be a positive integer"

    Scenario: List of Function keys
        Given there are users with infos:
            | firstname | lastname | number | context |
            | Fodé      | Bangoura | 1833   | default |
        Given I have a speeddial func key for user "Fodé" "Bangoura"
        When I request the list of func keys via RESTAPI
        Then I get a response with status "200"
        Then the list contains a speeddial func key for user "Fodé" "Bangoura"

    Scenario: List of Function keys with limit
        Given there are users with infos:
            | firstname | lastname | number | context |
            | Fodé      | Bangoura | 1749   | default |
            | Bountrabi | Sylla    | 1750   | default |
        Given I have a speeddial func key for user "Fodé" "Bangoura"
        Given I have a speeddial func key for user "Bountrabi" "Sylla"
        When I request the list of func keys with the following parameters via RESTAPI:
            | limit |
            | 1     |
        Then I get a response with status "200"
        Then I have a list with 1 results

    Scenario: Get a func key that does not exist
        Given there is no func key with id "725437"
        When I request the func key with id "725437" via RESTAPI
        Then I get a response with status "404"

    Scenario: Get a func key
        Given there are users with infos:
            | firstname | lastname  | number | context |
            | Fodé      | Sanderson | 1348   | default |
        Given I have a speeddial func key for user "Fodé" "Sanderson"
        When I request the funckey with a destination for user "Fodé" "Sanderson"
        Then I get a response with status "200"
        Then I get a response with a link to the "func_keys" resource
        Then I get a func key of type "speeddial"
        Then I get a func key with a destination id for user "Fodé" "Sanderson"

    Scenario: Creating a func key with invalid parameters
        When I create an empty func key via RESTAPI:
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: type,destination,destination_id"

        When I create the following func keys via RESTAPI:
            | unexisting_field |
            | unexisting_value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Creating a func key with a type that doesn't exist
        Given I have the following users:
            | id     | firstname | lastname |
            | 478009 | Lord      | Fodé     |
        When I create the following func keys via RESTAPI:
            | type      | destination | destination_id |
            | supertype | user        | 478009         |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: type supertype does not exist"

    Scenario: Creating a func key with a destination that doesn't exist
        Given I have the following users:
            | id     | firstname | lastname |
            | 848966 | Maestro   | Fodé     |
        When I create the following func keys via RESTAPI:
            | type      | destination      | destination_id |
            | speeddial | superdestination | 848966         |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: destination superdestination does not exist"

    Scenario: Creating a func key with a destination id that doesn't exist
        Given there are no users with id "168110"
        When I create the following func keys via RESTAPI:
            | type      | destination | destination_id |
            | speeddial | user        | 168110         |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: user with id=168110 does not exist"

    Scenario: Creating a func key with a destination for a user
        Given I have the following users:
            | id     | firstname | lastname |
            | 922545 | Ba        | Fodé     |
        When I create the following func keys via RESTAPI:
            | type      | destination | destination_id |
            | speeddial | user        | 922545         |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "func_keys" resource
        Then I get a response with a link to the "func_keys" resource
        Then I have the following func keys via RESTAPI:
            | type      | destination | destination_id |
            | speeddial | user        | 922545         |

    Scenario: Creating 2 func keys with same destination
        Given I have the following users:
            | id     | firstname | lastname |
            | 389369 | Fodé      | Enzo     |
        When I create the following func keys via RESTAPI:
            | type      | destination | destination_id |
            | speeddial | user        | 389369         |
        Then I get a response with status "201"
        When I create the following func keys via RESTAPI:
            | type      | destination | destination_id |
            | speeddial | user        | 389369         |
        Then I get a response with status "201"
