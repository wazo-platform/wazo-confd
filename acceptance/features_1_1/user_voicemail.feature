Feature: Associate a user and a voicemail

    Scenario: Associate a user with a voicemail that doesn't exist
        Given I have no voicemail with id "1000"
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Kathryn   | Janeway  | 1060   | default | sip      |
        When I associate user "Kathryn Janeway" with voicemail id "1000" via RESTAPI
        Then I get a response with status "400"
        Then I get an error message matching "Nonexistent parameters: voicemail \d+ does not exist"

    Scenario: Associate a user that doesn't exist with a voicemail
        Given I have the following voicemails:
            | name             | number | context |
            | Samantha Wildman | 1071   | default |
        When I associate a fake user with with voicemail "1071@default" via RESTAPI
        Then I get a response with status "404"
        Then I get an error message matching "Nonexistent parameters: user with \d+ does not exist"

    Scenario: Associate a voicemail with a user that has no line
        Given there are users with infos:
            | firstname | lastname |
            | Chakotay  | Marquis  |
        Given I have the following voicemails:
            | name             | number | context |
            | Chakotay Marquis | 1061   | default |
        When I associate user "Chakotay Marquis" with voicemail "1061@default" via RESTAPI
        Then I get a response with status "400"
        Then I get an error message matching "Invalid parameters: user with id \d+ does not have any line"

    Scenario: Associate a voicemail with a user that has a SIP line
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Tuvok     | Vulcan   | 1063   | default | sip      |
        Given I have the following voicemails:
            | name            | number | context |
            | Tuvok Vulcan    | 1063   | default |
        When I associate user "Tuvok Vulcan" with voicemail "1063@default" via RESTAPI
        Then I get a response with status "201"
        Then I get a response with a voicemail id
        Then I get a response with a user id
        Then I get a header with a location matching "/1.1/users/\d+/voicemail"
        Then I get a response with a link to the "voicemails" resource using the id "voicemail_id"
        Then I get a response with a link to the "users" resource using the id "user_id"

    Scenario: Associate a voicemail with a user that has an SCCP line
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Tom       | Paris    | 1064   | default | sccp     |
        Given I have the following voicemails:
            | name      | number | context |
            | Tom Paris | 1064   | default |
        When I associate user "Tom Paris" with voicemail "1064@default" via RESTAPI
        Then I get a response with status "201"
        Then I get a response with a voicemail id
        Then I get a response with a user id
        Then I get a header with a location matching "/1.1/users/\d+/voicemail"
        Then I get a response with a link to the "voicemails" resource using the id "voicemail_id"
        Then I get a response with a link to the "users" resource using the id "user_id"

    Scenario: Associate a voicemail with a user that has a custom line
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Harry     | Kim      | 1065   | default | custom   |
        Given I have the following voicemails:
            | name      | number | context |
            | Harry Kim | 1065   | default |
        When I associate user "Harry Kim" with voicemail "1065@default" via RESTAPI
        Then I get a response with status "201"
        Then I get a response with a voicemail id
        Then I get a response with a user id
        Then I get a header with a location matching "/1.1/users/\d+/voicemail"
        Then I get a response with a link to the "voicemails" resource using the id "voicemail_id"
        Then I get a response with a link to the "users" resource using the id "user_id"

    Scenario: Associate a voicemail with a user that already has one
        Given there are users with infos:
            | firstname | lastname | number | context | protocol | voicemail_name  | voicemail_number |
            | B'Elanna  | Torres   | 1065   | default | sip      | B'Elanna Torres | 1065             |
        When I associate user "B'Elanna Torres" with voicemail "1065@default" via RESTAPI
        Then I get a response with status "400"
        Then I get an error message matching "Invalid parameters: user with id \d+ already has a voicemail"

    Scenario: Get voicemail association when it doesn't exist
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Neelix    | Talaxian | 1066   | default | sip      |
        When I request the voicemail associated to user "Neelix" "Talaxian" via RESTAPI
        Then I get a response with status "404"
        Then I get an error message matching "User with id=\d+ does not have a voicemail"

    Scenario: Get voicemail association when user has a voicemail
        Given there are users with infos:
            | firstname | lastname | number | context | protocol | voicemail_name | voicemail_number |
            | Kes       | Ocampan  | 1067   | default | sip      | Kes Ocampan    | 1067             |
        When I request the voicemail associated to user "Kes" "Ocampan" via RESTAPI
        Then I get a response with status "200"
        Then I get a response with a voicemail id
        Then I get a response with a user id
        Then I get a response with a link to the "voicemails" resource using the id "voicemail_id"
        Then I get a response with a link to the "users" resource using the id "user_id"

    Scenario: Get voicemail association when user does not exist
        Given there are no users with id "9999"
        When I request the voicemail associated to user with id "9999" via RESTAPI
        Then I get a response with status "404"
        Then I get an error message "User with id=9999 does not exist"

    Scenario: Dissociate a user that has a SIP line from his voicemail
        Given there are users with infos:
            | firstname | lastname | number | context | protocol | voicemail_name  | voicemail_number |
            | Doctor    | Hologram | 1068   | default | sip      | Doctor Hologram | 1068             |
        When I dissociate user "Doctor" "Hologram" from his voicemail via RESTAPI
        Then I get a response with status "204"

     Scenario: Dissociate a user that has a SCCP line from his voicemail
        Given there are users with infos:
            | firstname | lastname | number | context | protocol | voicemail_name | voicemail_number |
            | Seven     | Of Nine  | 1069   | default | sccp     | Seven Of Nine  | 1069             |
        When I dissociate user "Seven" "Of Nine" from his voicemail via RESTAPI
        Then I get a response with status "204"

    Scenario: Dissociate a user that has a custom line from his voicemail
        Given there are users with infos:
            | firstname | lastname  | number | context | protocol | voicemail_name  | voicemail_number |
            | Seska     | Cardacian | 1070   | default | custom   | Seska Cardacian | 1070             |
        When I dissociate user "Seska" "Cardacian" from his voicemail via RESTAPI
        Then I get a response with status "204"

    Scenario: Dissociate a voicemail from a user that does not exist
        Given there are no users with id "9999"
        When I dissociate user with id "9999" from his voicemail via RESTAPI
        Then I get a response with status "404"
        Then I get an error message "User with id=9999 does not exist"

    Scenario: Dissociate a voicemail from a user that has no voicemail
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Naomi     | Wildman  | 1071   | default | sip      |
        When I dissociate user "Naomi" "Wildman" from his voicemail via RESTAPI
        Then I get a response with status "404"
        Then I get an error message matching "User with id=\d+ does not have a voicemail"
