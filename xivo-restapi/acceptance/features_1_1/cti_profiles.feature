Feature: REST API CTI Profiles

    Scenario: CTI Profiles list
        Given I have the following CTI profiles:
            |  id |      name |
            | 110 | Profil 00 |
        When I access the list of CTI profiles
        Then I get a list containing the following CTI profiles:
            |  id |      name |
            | 110 | Profil 00 |

    Scenario: Get a single CTI profile
        Given I have the following CTI profiles:
            |  id |      name |
            | 111 | Profil 00 |
        When I ask for the CTI profile with id "111"
        Then I get a response with status "200"
        Then I get a CTI profile with the following parameters:
            |  id |      name |
            | 111 | Profil 00 |

    Scenario: Get a CTI profile that does not exist
        Given there is no CTI profile with id "215"
        When I ask for the CTI profile with id "215"
        Then I get a response with status "404"

    Scenario: Associate CTI profile to user
        Given there are users with infos:
            | firstname | lastname |
            |  Genviève |    Camus |
        Given I have the following CTI profiles:
            |  id |     name  |
            | 113 | Profil 02 |
        When I associate CTI profile "113" with user "Genviève" "Camus"
        Then I get a response with status "201"
        Then I get a response with a link to the "users" resource using the id "user_id"
        Then I get a response with a link to the "cti_profiles" resource using the id "cti_profile_id"

    Scenario: Get CTI profile associated to a user
        Given there are users with infos:
            | firstname | lastname |
            |      Eric |  Lerouge |
        Given I have the following CTI profiles:
            |  id |      name |
            | 112 | Profil 01 |
        Given the following users, CTI profiles are linked:
            | user_fullname | cti_profile_id |
            |  Eric Lerouge |            112 |
        When I send request for the CTI profile associated to the user "Eric" "Lerouge"
        Then I get a response with status "200"
        Then I get a response with a link to the "users" resource using the id "user_id"
        Then I get a response with a link to the "cti_profiles" resource using the id "cti_profile_id"

    Scenario: Get CTI profile from a user who doesn't have one
        Given there are users with infos:
            | firstname | lastname |
            |    Marcel |     Aymé |
        When I send request for the CTI profile associated to the user "Marcel" "Aymé"
        Then I get a response with status "404"
        Then I get an error message matching "User with id=\d+ does not have a CTI profile"

    Scenario: Dissociate CTI profile from a user
        Given there are users with infos:
            | firstname | lastname |
            |      Marc |  Desnoix |
        Given I have the following CTI profiles:
            |  id |      name |
            | 114 | Profil 03 |
        Given the following users, CTI profiles are linked:
            | user_fullname | cti_profile_id |
            |  Marc Desnoix |            114 |
        When I dissociate the user "Marc" "Desnoix" from its CTI profile
        Then I get a response with status "204"

    Scenario: Associate a user to a CTI profile which does not exist
        Given there are users with infos:
            | firstname | lastname |
            |    Cécile |   Durand |
        Given there is no CTI profile with id "117"
        When I associate CTI profile "117" with user "Cécile" "Durand"
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: cti_profile 117 does not exist"

    Scenario: Associate a CTI profile to a user that already has one
        Given there are users with infos:
            | firstname |   lastname |
            |    Gaston |    Bernard |
        Given I have the following CTI profiles:
            |  id |      name |
            | 117 | Profil 06 |
            | 118 | Profil 07 |
        Given the following users, CTI profiles are linked:
            |   user_fullname | cti_profile_id |
            |  Gaston Bernard |            117 |
        When I associate CTI profile "118" with user "Gaston" "Bernard"
        Then I get a response with status "400"
        Then I get an error message matching "Invalid parameters: user with id \d+ already has a CTI profile"

