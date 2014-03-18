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

    Scenario: List of Function keys with search
        Given there is a group "balletnational" with extension "2392@default"
        Given I have the following users:
            | firstname | lastname |
            | Mao       | Abdoulai |

        When I request the list of func keys with the following parameters via RESTAPI:
            | search |
            | user   |
        Then the list contains the following func keys:
            | type      | destination | destination name |
            | speeddial | user        | Mao Abdoulai     |

        When I request the list of func keys with the following parameters via RESTAPI:
            | search |
            | group  |
        Then the list contains the following func keys:
            | type      | destination | destination name |
            | speeddial | group       | balletnational   |

    Scenario: List of Function keys with order and direction
        Given there is a group "balletnational" with extension "2392@default"
        Given I have the following users:
            | firstname | lastname |
            | Mao       | Abdoulai |

        When I request the list of func keys with the following parameters via RESTAPI:
            | order       | direction |
            | destination | asc       |
        Then the list contains the following func keys in the right order:
            | type      | destination | destination name |
            | speeddial | group       | balletnational   |
            | speeddial | user        | Mao Abdoulai     |

        When I request the list of func keys with the following parameters via RESTAPI:
            | order       | direction  |
            | destination | desc       |
        Then the list contains the following func keys in the right order:
            | type      | destination | destination name |
            | speeddial | user        | Mao Abdoulai     |
            | speeddial | group       | balletnational   |

    Scenario: List of Function keys with limit and skip
        Given there is a group "danseurscorontine" with extension "2744@default"
        Given I have the following users:
            | firstname | lastname |
            | Bountrabi | Sylla    |

        When I request the list of func keys with the following parameters via RESTAPI:
            | limit | order       |
            | 1     | id          |
        Then I have a list with 1 results

        When I memorize the first entry in the list
        When I request the list of func keys with the following parameters via RESTAPI:
            | limit | skip | order       |
            | 1     | 1    | id          |
        Then I have a list with 1 results
        Then the memorized entry is not in the list

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
        Then I get a response with status "200"
        Then the list does not contain the following func keys:
            | type      | destination | destination name |
            | speeddial | group       | salifkeita       |

    Scenario: Creating a queue adds a func key to the list
        Given there is no queue with number "3658"
        When I create the following queues:
            | name    | display name | number | context |
            | lafoire | La Foire     | 3658   | default |
        When I request the list of func keys via RESTAPI
        Then I get a response with status "200"
        Then the list contains the following func keys:
            | type      | destination | destination name |
            | speeddial | queue       | lafoire          |

    Scenario: Deleting a queue removes a func key from the list
        Given there are queues with infos:
            | name    | display name | number | context |
            | cellcom | Cell Com     | 3288   | default |
        When I delete the queue with number "3288"
        When I request the list of func keys via RESTAPI
        Then I get a response with status "200"
        Then the list does not contain the following func keys:
            | type      | destination | destination name |
            | speeddial | queue       | cellcom          |

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
