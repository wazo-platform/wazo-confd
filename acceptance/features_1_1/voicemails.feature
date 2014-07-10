Feature: REST API Voicemails

    Scenario: Get a voicemail that doesn't exist
        Given I have no voicemail with id "214773"
        When I request voicemail with id "214773"
        Then I get a response with status "404"

    Scenario: Get a voicemail
        Given I have the following voicemails:
            | name            | number | context |
            | Jean-Luc Picard | 1000   | default |
        When I send a request for the voicemail "1000@default", using its id
        Then I get a response with status "200"
        Then I get a response with a link to the "voicemails" resource
        Then I have the following voicemails via RESTAPI:
            | name            | number | context | attach_audio | delete_messages | ask_password |
            | Jean-Luc Picard | 1000   | default | false        | false           | true         |

    Scenario: Get a voicemail with all parameters
        Given I have the following voicemails:
            | name          | number | context | password | email            | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | William Riker | 1001   | default | 1234     | test@example.com | en_US    | eu-fr    | 100          | true         | false           | false        |
        When I send a request for the voicemail "1001@default", using its id
        Then I get a response with status "200"
        Then I get a response with a link to the "voicemails" resource
        Then I have the following voicemails via RESTAPI:
            | name          | number | context | password | email            | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | William Riker | 1001   | default | 1234     | test@example.com | en_US    | eu-fr    | 100          | true         | false           | false        |

    Scenario: Voicemail list
        Given I have the following voicemails:
            | name            | number | context | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | Geordi La Forge | 1002   | default | en_US    | eu-fr    | 100          | true         | false           | true         |
            | Tasha Yar       | 1003   | default | fr_FR    | eu-fr    | 10           | false        | true            | false        |
        When I request the list of voicemails via RESTAPI
        Then I get a response with status "200"
        Then I get a list containing the following voicemails via RESTAPI:
            | name            | number | context | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | Geordi La Forge | 1002   | default | en_US    | eu-fr    | 100          | true         | false           | true         |
            | Tasha Yar       | 1003   | default | fr_FR    | eu-fr    | 10           | false        | true            | false        |

    Scenario: Creating an empty voicemail
        When I create an empty voicemail via RESTAPI:
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: name,number,context"

    Scenario: Creating a voicemail with parameters that don't exist
        When I create the following voicemails via RESTAPI:
          | unexisting_field |
          | unexisting_value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Creating a voicemail with a name and parameters that don't exist
        When I create the following voicemails via RESTAPI:
          | name       | unexisting_field |
          | Joe Dahool | unexisting_value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Creating two voicemails with the same number and context
        Given there is no voicemail with number "1001" and context "default"
        Given I have the following voicemails:
            | name      | number | context |
            | Worm Hole | 1001   | default |
        When I create the following voicemails via RESTAPI:
          | name          | number | context |
          | Roberto Vegas | 1001   | default |
        Then I get a response with status "400"
        Then I get an error message "Voicemail 1001@default already exists"

    Scenario: Creating a voicemail with a invalid password
        Given there is no voicemail with number "1001" and context "default"
        When I create the following voicemails via RESTAPI:
          | name       | number | context | password |
          | Joe Dahool | 1001   | default | toto     |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: password"

    Scenario: Creating a voicemail with a non existent context
        Given there is no voicemail with number "1001" and context "default"
        When I create the following voicemails via RESTAPI:
          | name       | number | context      |
          | Joe Dahool | 1001   | qwertyasdfgh |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: context qwertyasdfgh does not exist"

    Scenario: Creating a voicemail with a non existent language
        Given there is no voicemail with number "1001" and context "default"
        When I create the following voicemails via RESTAPI:
          | name       | number | context | language |
          | Joe Dahool | 1001   | default | qq_KK    |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: language qq_KK does not exist"

    Scenario: Creating a voicemail with a non existent timezone
        Given there is no voicemail with number "1001" and context "default"
        When I create the following voicemails via RESTAPI:
          | name       | number | context | timezone |
          | Joe Dahool | 1001   | default | qq-kk    |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: timezone qq-kk does not exist"

    Scenario: Creating a voicemail with a invalid parameter max_messages
        Given there is no voicemail with number "1001" and context "default"
        When I create the following voicemails via RESTAPI:
          | name       | number | context | max_messages |
          | Joe Dahool | 1001   | default | zero         |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: max_messages"
        When I create the following voicemails via RESTAPI:
          | name       | number | context | max_messages |
          | Joe Dahool | 1001   | default | -4           |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: max_messages"

    Scenario: Creating a voicemail with a invalid parameter number
        When I create the following voicemails via RESTAPI:
          | name       | number     | context |
          | Joe Dahool | mille deux | default |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: number"
        When I create the following voicemails via RESTAPI:
          | name       | number | context |
          | Joe Dahool | -54321 | default |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: number"

    Scenario: Creating a voicemail with required fields
        Given there is no voicemail with number "1000" and context "default"
        When I create the following voicemails via RESTAPI:
          | name       | number | context |
          | Joe Dahool | 1000   | default |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "voicemails" resource
        Then I get a response with a link to the "voicemails" resource
        Then I have the following voicemails via RESTAPI:
          | name       | number | context |
          | Joe Dahool | 1000   | default |

    Scenario: Creating a voicemail with all fields
        Given there is no voicemail with number "1000" and context "default"
        When I create the following voicemails via RESTAPI:
          | name       | number | context | password | email          | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
          | Joe Dahool | 1000   | default | 1234     | joe@dahool.com | fr_FR    | eu-fr    | 50           | true         | false           | false        |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "voicemails" resource
        Then I get a response with a link to the "voicemails" resource
        Then I have the following voicemails via RESTAPI:
          | name       | number | context | password | email          | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
          | Joe Dahool | 1000   | default | 1234     | joe@dahool.com | fr_FR    | eu-fr    | 50           | true         | false           | false        |

    Scenario: Creating two voicemails with the same number but different context
        Given there is no voicemail with number "1000" and context "default"
        Given there is no voicemail with number "1000" and context "statscenter"
        When I create the following voicemails via RESTAPI:
          | name       | number | context     |
          | Joe Dahool | 1000   | default     |
        Then I get a response with status "201"
        Then I have the following voicemails via RESTAPI:
          | name       | number | context     |
          | Joe Dahool | 1000   | default     |
        When I create the following voicemails via RESTAPI:
          | name       | number | context     |
          | Kim Jung   | 1000   | statscenter |
        Then I get a response with status "201"
        Then I have the following voicemails via RESTAPI:
          | name       | number | context     |
          | Kim Jung   | 1000   | statscenter |

    Scenario: Delete a voicemail that does not exist
        Given there is no voicemail with number "1030" and context "default"
        When I delete voicemail "1030@default" via RESTAPI
        Then I get a response with status "404"

    Scenario: Delete a voicemail associated to nothing
        Given I have the following voicemails:
            | name       | number | context | email                      |
            | Jadzia Dax | 1031   | default | jadzia.dax@deep.space.nine |
        When I delete voicemail "1031@default" via RESTAPI
        Then I get a response with status "204"
        Then voicemail with number "1031" no longer exists

    Scenario: Delete a voicemail associated to a user with a SIP line
        Given there are users with infos:
            | firstname | lastname | language | number | context | protocol | voicemail_name | voicemail_number |
            | Miles     | O'Brien  | en_US    | 1032   | default | sip      | Miles O'Brien  | 1032             |
        When I delete voicemail "1032@default" via RESTAPI
        Then I get a response with status "400"
        Then I get an error message "Error while deleting voicemail: Cannot delete a voicemail associated to a user"

    Scenario: Delete a voicemail associated to a user with a SCCP line
        Given there are users with infos:
            | firstname | lastname | language | number | context | protocol | voicemail_name | voicemail_number |
            | Kurn      | Klingon  | en_US    | 1033   | default | sccp     | Kurn Klingon   | 1033             |
        When I delete voicemail "1033@default" via RESTAPI
        Then I get a response with status "400"
        Then I get an error message "Error while deleting voicemail: Cannot delete a voicemail associated to a user"

    Scenario: Delete a voicemail associated to an incoming call
        Given I have the following voicemails:
            | name       | number | context |
            | Jake Sisko | 1034   | default |
        Given there is an incall "1034" in context "from-extern" to the "Voicemail" "1034@default"
        When I delete voicemail "1034@default" via RESTAPI
        Then I get a response with status "204"
        Then incall "1034" is associated to nothing

    Scenario: Edit a voicemail that does not exist
        Given there is no voicemail with number "2345" and context "default"
        When I edit voicemail "2345@default" via RESTAPI:
            | name |
            | toto |
        Then I get a response with status "404"

    Scenario: Edit a voicemail with parameters that don't exist
        Given I have the following voicemails:
            | name       | number | context | email                      |
            | Jadzia Dax | 1031   | default | jadzia.dax@deep.space.nine |
        When I edit voicemail "1031@default" via RESTAPI:
            | unexisting_field |
            | unexisting_value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Edit a voicemail with a name and parameters that don't exist
        Given I have the following voicemails:
            | name       | number | context | email                      |
            | Jadzia Dax | 1031   | default | jadzia.dax@deep.space.nine |
        When I edit voicemail "1031@default" via RESTAPI:
            | name       | unexisting_field |
            | Joe Dahool | unexisting_value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Edit two voicemails with the same number and context
        Given I have the following voicemails:
            | name         | number | context | email                      |
            | Jadzia Dax   | 4732   | default | jadzia.dax@deep.space.nine |
            | Kim Jung Hui | 3796   | default | kim.jung@hui.cdn           |
        When I edit voicemail "4732@default" via RESTAPI:
            | name          | number | context |
            | Roberto Vegas | 3796   | default |
        Then I get a response with status "400"
        Then I get an error message "Voicemail 3796@default already exists"

    Scenario: Edit a voicemail with a invalid password
        Given I have the following voicemails:
            | name       | number | context | email                      |
            | Jadzia Dax | 1021   | default | jadzia.dax@deep.space.nine |
        When I edit voicemail "1021@default" via RESTAPI:
            | password |
            | toto     |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: password"

    Scenario: Edit a voicemail with a non existent context
        Given I have the following voicemails:
            | name       | number | context | email                      |
            | Jadzia Dax | 2345   | default | jadzia.dax@deep.space.nine |
        When I edit voicemail "2345@default" via RESTAPI:
            | context      |
            | qwertyasdfgh |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: context qwertyasdfgh does not exist"

    Scenario: Edit a voicemail with a non existent language
        Given I have the following voicemails:
            | name       | number | context | email                      |
            | Jadzia Dax | 6789   | default | jadzia.dax@deep.space.nine |
        When I edit voicemail "6789@default" via RESTAPI:
            | language |
            | qq_KK    |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: language qq_KK does not exist"

    Scenario: Edit a voicemail with a non existent timezone
        Given I have the following voicemails:
            | name       | number | context | email                      |
            | Jadzia Dax | 3987   | default | jadzia.dax@deep.space.nine |
        When I edit voicemail "3987@default" via RESTAPI:
            | timezone |
            | qq-kk    |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: timezone qq-kk does not exist"

    Scenario: Edit a voicemail with a invalid parameter max_messages
        Given I have the following voicemails:
            | name       | number | context | email                      |
            | Jadzia Dax | 2568   | default | jadzia.dax@deep.space.nine |
        When I edit voicemail "2568@default" via RESTAPI:
            | max_messages |
            | zero         |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: max_messages"
        When I edit voicemail "2568@default" via RESTAPI:
            | max_messages |
            | -5           |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: max_messages"

    Scenario: Edit a voicemail with a invalid parameter number
        Given I have the following voicemails:
            | name       | number | context | email                      |
            | Jadzia Dax | 2854   | default | jadzia.dax@deep.space.nine |
        When I edit voicemail "2854@default" via RESTAPI:
            | number     |
            | mille deux |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: number"
        When I edit voicemail "2854@default" via RESTAPI:
            | number |
            | -54321 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: number"

    Scenario: Edit a voicemail with required fields
        Given there is no voicemail with number "1000" and context "default"
        Given I have the following voicemails:
            | name       | number | context | email                      |
            | Jadzia Dax | 1598   | default | jadzia.dax@deep.space.nine |
        When I edit voicemail "1598@default" via RESTAPI:
            | name       | number | context |
            | Joe Dahool | 1000   | default |
        Then I get a response with status "204"
        When I send a request for the voicemail "1000@default", using its id
        Then I have the following voicemails via RESTAPI:
            | name       | number | context | email                      |
            | Joe Dahool | 1000   | default | jadzia.dax@deep.space.nine |

    Scenario: Edit a voicemail with all fields
        Given there is no voicemail with number "1000" and context "default"
        Given I have the following voicemails:
            | name       | number | context | password | email          | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | Super Hero | 2000   | default | 4566     | ggd@gfggdd.com | en_US    | eu-fr    | 10           | false        | true            | true         |
        When I edit voicemail "2000@default" via RESTAPI:
            | name       | number | context | password | email          | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | Joe Dahool | 1000   | default | 1234     | joe@dahool.com | fr_FR    | eu-fr    | 50           | true         | false           | false        |
        Then I get a response with status "204"
        When I send a request for the voicemail "1000@default", using its id
        Then I have the following voicemails via RESTAPI:
            | name       | number | context | password | email          | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | Joe Dahool | 1000   | default | 1234     | joe@dahool.com | fr_FR    | eu-fr    | 50           | true         | false           | false        |

    Scenario: Edit two voicemails with the same number but different context
        Given there is no voicemail with number "1001" and context "default"
        Given there is no voicemail with number "2001" and context "statscenter"
        Given I have the following voicemails:
            | name       | number | context     |
            | Joe Dahool | 1000   | default     |
            | Joe Dahool | 2000   | statscenter |
        When I edit voicemail "1000@default" via RESTAPI:
            | name       | number | context     |
            | Joe Dahool | 1001   | default     |
        Then I get a response with status "204"
        When I send a request for the voicemail "1001@default", using its id
        Then I have the following voicemails via RESTAPI:
            | name       | number | context     |
            | Joe Dahool | 1001   | default     |
        When I edit voicemail "2000@statscenter" via RESTAPI:
            | name       | number | context     |
            | Kim Jung   | 2001   | statscenter |
        Then I get a response with status "204"
        When I send a request for the voicemail "2001@statscenter", using its id
        Then I have the following voicemails via RESTAPI:
            | name       | number | context     |
            | Kim Jung   | 2001   | statscenter |

    Scenario: Edit a voicemail associated to a user with a SIP line
        Given there is no voicemail with number "1051" and context "default"
        Given there are users with infos:
            | firstname | lastname | language | number | context | protocol | voicemail_name | voicemail_number |
            | Miles     | O'Brien  | en_US    | 1050   | default | sip      | Miles O'Brien  | 1050             |
        When I edit voicemail "1050@default" via RESTAPI:
            | number |
            | 1051   |
        Then I get a response with status "400"
        Then I get an error message "Error while editing voicemail: Cannot edit a voicemail associated to a user"

    Scenario: Edit a voicemail associated to a user with a SCCP line
        Given there is no voicemail with number "1052" and context "default"
        Given there is no voicemail with number "1053" and context "default"
        Given there are users with infos:
            | firstname | lastname | language | number | context | protocol | voicemail_name | voicemail_number |
            | Worf      | Klingon  | en_US    | 1052   | default | sccp     | Worf Klingon   | 1052             |
        When I edit voicemail "1052@default" via RESTAPI:
            | number |
            | 1053   |
        Then I get a response with status "400"
        Then I get an error message "Error while editing voicemail: Cannot edit a voicemail associated to a user"
