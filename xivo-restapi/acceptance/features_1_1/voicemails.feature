Feature: REST API Voicemails

    Scenario: Get a voicemail that doesn't exist
        Given I have no voicemail with id "10"
        When I request voicemail with id "10"
        Then I get a response with status "404"

    Scenario: Get a voicemail
        Given I have the following voicemails:
            | name            | number | context |
            | Jean-Luc Picard | 1000   | default |
        When I send a request for the voicemail with number "1000", using its id
        Then I get a response with status "200"
        Then I get a response with a link to the "voicemails" resource
        Then the voicemail has the following parameters:
            | name            | number | context | attach_audio | delete_messages | ask_password |
            | Jean-Luc Picard | 1000   | default | false        | false           | false        |

    Scenario: Get a voicemail with all parameters
        Given I have the following voicemails:
            | name          | number | context | password | email            | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | William Riker | 1001   | default | 1234     | test@example.com | en_US    | eu-fr    | 100          | true         | false           | true         |
        When I send a request for the voicemail with number "1001", using its id
        Then I get a response with status "200"
        Then I get a response with a link to the "voicemails" resource
        Then the voicemail has the following parameters:
            | name          | number | context | password | email            | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | William Riker | 1001   | default | 1234     | test@example.com | en_US    | eu-fr    | 100          | true         | false           | true         |

    Scenario: Voicemail list
        Given I have the following voicemails:
            | name            | number | context | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | Geordi La Forge | 1002   | default | en_US    | eu-fr    | 100          | true         | false           | true         |
            | Tasha Yar       | 1003   | default | fr_FR    | eu-fr    | 10           | false        | true            | false        |
        When I request the list of voicemails
        Then I get a response with status "200"
        Then I get a list containing the following voicemails:
            | name            | number | context | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | Geordi La Forge | 1002   | default | en_US    | eu-fr    | 100          | true         | false           | true         |
            | Tasha Yar       | 1003   | default | fr_FR    | eu-fr    | 10           | false        | true            | false        |

    Scenario: Voicemail list with invalid order parameter
        When I request the list of voicemails with the following parameters:
            | order |
            | toto  |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: ordering column 'toto' does not exist"

    Scenario: Voicemail list with invalid direction parameter
        When I request the list of voicemails with the following parameters:
            | direction |
            | toto      |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: direction must be asc or desc"

    Scenario: Voicemail list with invalid limit parameter
        When I request the list of voicemails with the following parameters:
            | limit |
            | -32   |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: limit must be a positive integer"
        When I request the list of voicemails with the following parameters:
            | limit |
            | asdf  |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: limit must be a positive integer"

    Scenario: Voicemail list with invalid limit parameter
        When I request the list of voicemails with the following parameters:
            | skip |
            | -32  |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: skip must be a positive integer"
        When I request the list of voicemails with the following parameters:
            | skip |
            | asdf |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: skip must be a positive integer"

    Scenario: Voicemail list with order
        Given I have the following voicemails:
            | name | number | context |
            | Data | 1005   | default |
            | Warf | 1004   | default |
        When I request the list of voicemails with the following parameters:
            | order  |
            | number |
        Then I get a response with status "200"
        Then I get a list of voicemails in the following order:
            | name | number | context |
            | Warf | 1004   | default |
            | Data | 1005   | default |
        When I request the list of voicemails with the following parameters:
            | order |
            | name  |
        Then I get a response with status "200"
        Then I get a list of voicemails in the following order:
            | name | number | context |
            | Data | 1005   | default |
            | Warf | 1004   | default |

    Scenario: Voicemail list with order and direction
        Given I have the following voicemails:
            | name            | number | context | max_messages | language |
            | Wesley Crusher  | 1008   | default | 50           | es_ES    |
            | Deanna Troi     | 1007   | default | 100          | fr_FR    |
            | Beverly Crusher | 1006   | default | 15           | en_US    |
        When I request the list of voicemails with the following parameters:
            | order | direction |
            | name  | desc      |
        Then I get a response with status "200"
        Then I get a list of voicemails in the following order:
            | name            | number | context | max_messages | language |
            | Wesley Crusher  | 1008   | default | 50           | es_ES    |
            | Deanna Troi     | 1007   | default | 100          | fr_FR    |
            | Beverly Crusher | 1006   | default | 15           | en_US    |
        When I request the list of voicemails with the following parameters:
            | order    | direction |
            | language | asc       |
        Then I get a response with status "200"
        Then I get a list of voicemails in the following order:
            | name            | number | context | max_messages | language |
            | Beverly Crusher | 1006   | default | 15           | en_US    |
            | Wesley Crusher  | 1008   | default | 50           | es_ES    |
            | Deanna Troi     | 1007   | default | 100          | fr_FR    |

    Scenario: Voicemail list with limit
        Given I have the following voicemails:
            | name  | number | context |
            | Sarek | 1009   | default |
            | Spock | 1010   | default |
        When I request the list of voicemails with the following parameters:
            | limit |
            | 2     |
        Then I get a response with status "200"
        Then I have a list with 2 results
        Then the list contains the same total voicemails as on the server

    Scenario: Voicemail list with skip and ordering
        Given I have the following voicemails:
            | name               | number | context |
            | Alyssa Ogawa       | 2      | default |
            | Alexander Rozhenko | 1      | default |
        When I request the list of voicemails with the following parameters:
            | skip | order  | direction |
            | 1    | number | asc       |
        Then I get a response with status "200"
        Then I get a list of voicemails in the following order:
            | name         | number | context |
            | Alyssa Ogawa | 2      | default |
        Then I do not have the following voicemails in the list:
            | name               | number | context |
            | Alexander Rozhenko | 1      | default |

    Scenario: Voicemail list with pagination and ordering
        Given I have the following voicemails:
            | name          | number | context |
            | Keiko O'Brien | 9996   | default |
            | Guinan        | 9997   | default |
            | Lwxana Troi   | 9998   | default |
            | Ro Laren      | 9999   | default |
        When I request the list of voicemails with the following parameters:
            | limit | skip | order  | direction |
            | 2     | 1    | number | desc      |
        Then I get a response with status "200"
        Then I have a list with 2 results
        Then I get a list of voicemails in the following order:
            | name        | number | context |
            | Lwxana Troi | 9998   | default |
            | Guinan      | 9997   | default |
        Then I do not have the following voicemails in the list:
            | name          | number | context |
            | Keiko O'Brien | 9996   | default |
            | Ro Laren      | 9999   | default |

    Scenario: Voicemail list with search
        Given I have the following voicemails:
            | name             | number | context | email                           |
            | Gowron           | 1011   | default | gowron@uss.enterprise           |
            | Q                | 1012   | default | q@continuum.universe            |
            | Reginald Barclay | 1013   | default | reginald.barclay@uss.enterprise |
        When I request the list of voicemails with the following parameters:
            | search | 
            | reg    |
        Then I get a response with status "200"
        Then I get a list containing the following voicemails:
            | name             | number | context | email                           |
            | Reginald Barclay | 1013   | default | reginald.barclay@uss.enterprise |
        When I request the list of voicemails with the following parameters:
            | search     |
            | ENTERPRISE |
        Then I get a response with status "200"
        Then I get a list containing the following voicemails:
            | name             | number | context | email                           |
            | Reginald Barclay | 1013   | default | reginald.barclay@uss.enterprise |
            | Gowron           | 1011   | default | gowron@uss.enterprise           |
        When I request the list of voicemails with the following parameters:
            | search |
            | 1012   |
        Then I get a response with status "200"
        Then I get a list containing the following voicemails:
            | name             | number | context | email                           |
            | Q                | 1012   | default | q@continuum.universe            |

    Scenario: Voicemail list with search, pagination and ordering
        Given I have the following voicemails:
            | name           | number | context | email                          |
            | Benjamin Sisko | 1014   | default | benjamin.cisco@deep.space.nine |
            | Kira Nerys     | 1015   | default | kira.nerys@deep.space.nine     |
            | Odo            | 1016   | default | odo@deep.space.nine            |
            | Julian Bashir  | 1017   | default | julian.bashir@deep.space.nine  |
            | Worm Hole      | 1018   | default | worm.hole@space.universe       |
        When I request the list of voicemails with the following parameters:
            | search          | limit | skip | order  | direction |
            | deep.space.nine | 2     | 1    | number | desc      |
        Then I get a response with status "200"
        Then I get a list of voicemails in the following order:
            | name       | number | context | email                      |
            | Odo        | 1016   | default | odo@deep.space.nine        |
            | Kira Nerys | 1015   | default | kira.nerys@deep.space.nine |
        Then I do not have the following voicemails in the list:
            | name           | number | context | email                          |
            | Benjamin Sisko | 1014   | default | benjamin.cisco@deep.space.nine |
            | Julian Bashir  | 1017   | default | julian.bashir@deep.space.nine  |
            | Worm Hole      | 1018   | default | worm.hole@space.universe       |
        Then I have a list with 2 of 4 results

    Scenario: Delete a voicemail that does not exist
        Given there is no voicemail with number "1030" and context "default"
        When I delete voicemail with number "1030" via RESTAPI
        Then I get a response with status "404"

    Scenario: Delete a voicemail associated to nothing
        Given I have the following voicemails:
            | name       | number | context | email                      |
            | Jadzia Dax | 1030   | default | jadzia.dax@deep.space.nine |
        When I delete voicemail with number "1031" via RESTAPI
        Then I get a response with status "204"
        Then voicemail with number "1031" no longer exists

    Scenario: Delete a voicemail associated to a user with a SIP line
        Given there are users with infos:
            | firstname | lastname | language | number | context | protocol | voicemail_name | voicemail_number |
            | Miles     | O'Brien  | en_US    | 1032   | default | sip      | Miles O'Brien  | 1032             |
        When I delete voicemail with number "1032" via RESTAPI
        Then I get a response with status "400"
        Then I get an error message "Error while deleting voicemail: Cannot delete a voicemail associated to a user"

    Scenario: Delete a voicemail associated to a user with a SCCP line
        Given there are users with infos:
            | firstname | lastname | language | number | context | protocol | voicemail_name | voicemail_number |
            | Worf      | Klingon  | en_US    | 1033   | default | sccp     | Worf Klingon   | 1033             |
        When I delete voicemail with number "1033" via RESTAPI
        Then I get a response with status "400"
        Then I get an error message "Error while deleting voicemail: Cannot delete a voicemail associated to a user"

    Scenario: Delete a voicemail associated to an incoming call
        Given I have the following voicemails:
            | name       | number | context |
            | Jake Sisko | 1034   | default |
        Given there is an incall "1034" in context "from-extern" to the "Voicemail" "Jake Sisko (1034@default)"
        When I delete voicemail with number "1034" via RESTAPI
        Then I get a response with status "204"
        Then incall "1034" is associated to nothing
