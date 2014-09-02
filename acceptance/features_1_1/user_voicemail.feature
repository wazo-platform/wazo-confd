Feature: Associate a user and a voicemail

    Scenario: Associate a voicemail with a user that has a SIP line
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Tuvok     | Vulcan   | 1063   | default | sip      |
        Given I have the following voicemails:
            | name            | number | context |
            | Tuvok Vulcan    | 1063   | default |
        When I associate user "Tuvok Vulcan" with voicemail "1063@default" via CONFD
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
        When I associate user "Tom Paris" with voicemail "1064@default" via CONFD
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
        When I associate user "Harry Kim" with voicemail "1065@default" via CONFD
        Then I get a response with status "201"
        Then I get a response with a voicemail id
        Then I get a response with a user id
        Then I get a header with a location matching "/1.1/users/\d+/voicemail"
        Then I get a response with a link to the "voicemails" resource using the id "voicemail_id"
        Then I get a response with a link to the "users" resource using the id "user_id"

    Scenario: Get voicemail association when user has a voicemail
        Given there are users with infos:
            | firstname | lastname | number | context | protocol | voicemail_name | voicemail_number |
            | Kes       | Ocampan  | 1067   | default | sip      | Kes Ocampan    | 1067             |
        When I request the voicemail associated to user "Kes" "Ocampan" via CONFD
        Then I get a response with status "200"
        Then I get a response with a voicemail id
        Then I get a response with a user id
        Then I get a response with a link to the "voicemails" resource using the id "voicemail_id"
        Then I get a response with a link to the "users" resource using the id "user_id"

    Scenario: Dissociate a user that has a SIP line from his voicemail
        Given there are users with infos:
            | firstname | lastname | number | context | protocol | voicemail_name  | voicemail_number |
            | Doctor    | Hologram | 1068   | default | sip      | Doctor Hologram | 1068             |
        When I dissociate user "Doctor" "Hologram" from his voicemail via CONFD
        Then I get a response with status "204"

     Scenario: Dissociate a user that has a SCCP line from his voicemail
        Given there are users with infos:
            | firstname | lastname | number | context | protocol | voicemail_name | voicemail_number |
            | Seven     | Of Nine  | 1069   | default | sccp     | Seven Of Nine  | 1069             |
        When I dissociate user "Seven" "Of Nine" from his voicemail via CONFD
        Then I get a response with status "204"

    Scenario: Dissociate a user that has a custom line from his voicemail
        Given there are users with infos:
            | firstname | lastname  | number | context | protocol | voicemail_name  | voicemail_number |
            | Seska     | Cardacian | 1070   | default | custom   | Seska Cardacian | 1070             |
        When I dissociate user "Seska" "Cardacian" from his voicemail via CONFD
        Then I get a response with status "204"
