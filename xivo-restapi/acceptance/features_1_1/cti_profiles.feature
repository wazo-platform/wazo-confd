Feature: REST API CTI Profiles

    Scenario: CTI Profiles list
        Given I have the following CTI profiles:
           |  id |      name |
           | 110 | Profil 00 |
        When I acces the list of CTI profiles
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

    Scenario: CTI profile associated to a user
        Given I only have the following users:
            |     id | firstname | lastname |
            | 987961 |      Eric |  Lerouge |
        Given I have the following CTI profiles:
            |  id |      name |
            | 112 | Profil 01 |
        Given the following users, CTI profiles are linked:
            | user_id | cti_profile_id |
            |  987961 |            112 |
        When I send request for the CTI profile associated to the user id "987961"
        Then I get a response with status "200"
        Then I get a response with a link to the "users" resource using the id "user_id"
        Then I get a response with a link to the "cti_profiles" resource using the id "cti_profile_id"

    Scenario: User with no CTI profile
        Given I only have the following users:
            |     id | firstname | lastname |
            | 987962 |    Marcel |     Aymé |
        When I send request for the CTI profile associated to the user id "987962"
        Then I get a response with status "404"
        Then I get an error message "User with id=987962 does not have a CTI profile"

    Scenario: Associate CTI profile to user
        Given I only have the following users:
            |     id | firstname | lastname |
            | 987963 |  Genviève |    Camus |
        Given I have the following CTI profiles:
            |  id |     name  |
            | 113 | Profil 02 |
        When I associate CTI profile "113" with user "987963"
        Then I get a response with status "201"
        Then I get a response with a link to the "users" resource using the id "user_id"
        Then I get a response with a link to the "cti_profiles" resource using the id "cti_profile_id"

    Scenario: Dissociate CTI profile from a user
        Given I only have the following users:
            |     id | firstname | lastname |
            | 987964 |      Marc |  Desnoix |
        Given I have the following CTI profiles:
            |  id |      name |
            | 114 | Profil 03 |
        Given the following users, CTI profiles are linked:
            | user_id | cti_profile_id |
            |  987964 |            114 |
        When I dissociate the user "987964" from its CTI profile
        Then I get a response with status "204"

    Scenario: Associate a user to a CTI profile which does not exist
        Given I only have the following users:
            |     id | firstname | lastname |
            | 987966 |    Cécile |   Durand |
        When I associate CTI profile "117" with user "987966"
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: cti_profile_id 117 does not exist"

    Scenario: Associate a CTI profile to a user that already has one
        Given I only have the following users:
            |     id | firstname |   lastname |
            | 987967 |    Gaston |    Bernard |
        Given I have the following CTI profiles:
            |  id |      name |
            | 117 | Profil 06 |
            | 118 | Profil 07 |
        Given the following users, CTI profiles are linked:
            | user_id | cti_profile_id |
            |  987967 |            117 |
        When I associate CTI profile "118" with user "987967"
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: user with id 987967 already has a CTI profile"

