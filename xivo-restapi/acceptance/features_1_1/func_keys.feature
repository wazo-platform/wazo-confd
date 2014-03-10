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
        Given I have the following users:
            | firstname | lastname |
            | Fodé      | Bangoura |
        When I request the list of func keys via RESTAPI
        Then I get a response with status "200"
        Then the list contains the following func keys:
            | type      | destination | destination name |
            | speeddial | user        | Fodé Bangoura    |

    Scenario: List of Function keys with limit
        Given I have the following users:
            | firstname | lastname |
            | Fodé      | Bangoura |
            | Bountrabi | Sylla    |
        When I request the list of func keys with the following parameters via RESTAPI:
            | limit |
            | 1     |
        Then I get a response with status "200"
        Then I have a list with 1 results

    Scenario: Creating a user adds a func key to the list
        Given there is no user "Ninè" "Bangoura"
        When I create users with the following parameters:
            | firstname | lastname |
            | Ninè      | Bangoura |
        Then I get a response with status "201"
        When I request the list of func keys via RESTAPI
        Then I get a response with status "200"
        Then the list contains the following func keys:
            | type      | destination | destination name |
            | speeddial | user        | Ninè Bangoura    |

    Scenario: Deleting a user removes a func key from the list
        Given I have the following users:
            | firstname | lastname |
            | Moko      | Bangoura |
        When I delete the user with name "Moko" "Bangoura"
        Then I get a response with status "204"
        When I request the list of func keys via RESTAPI
        Then the list does not contain the following func keys:
            | type      | destination | destination name |
            | speeddial | user        | Moko Bangoura    |

    Scenario: Creating a group adds a func key to the list
        Given there is no group "guineeallstars"
        When I create a group "guineeallstars" with number "2968"
        When I request the list of func keys via RESTAPI
        Then I get a response with status "200"
        Then the list contains the following func keys:
            | type      | destination | destination name |
            | speeddial | group       | guineeallstars   |

    Scenario: Deleting a group removes a func key from the list
        Given there is a group "salifkeita" with extension "2548@default"
        When I remove the group "salifkeita"
        When I request the list of func keys via RESTAPI
        Then the list does not contain the following func keys:
            | type      | destination | destination name |
            | speeddial | group       | salifkeita       |

    Scenario: Get a func key that does not exist
        Given there is no func key with id "725437"
        When I request the func key with id "725437" via RESTAPI
        Then I get a response with status "404"

    Scenario: Get a func key
        Given I have the following users:
            | firstname | lastname  |
            | Fodé      | Sanderson |
        When I request the funckey with a destination for user "Fodé" "Sanderson"
        Then I get a response with status "200"
        Then I get a response with a link to the "func_keys" resource
        Then I get a func key of type "speeddial"
        Then I get a func key with a destination id for user "Fodé" "Sanderson"
