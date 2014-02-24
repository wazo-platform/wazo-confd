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
