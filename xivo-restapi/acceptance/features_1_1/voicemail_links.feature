Feature: Link a user and a voicemail

    Scenario: Link a user with a voicemail that doesn't exist
        Given I have no voicemail with id "1000"
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Kathryn   | Janeway  | 1060   | default | sip      |
        When I link user "Kathryn Janeway" with voicemail id "1000" via RESTAPI
        Then I get a response with status "400"
        Then I get an error message matching "Nonexistent parameters: voicemail \d+ does not exist"

    Scenario: Link a voicemail with a user that has no line
        Given there are users with infos:
            | firstname | lastname |
            | Chakotay  | Marquis  |
        Given I have the following voicemails:
            | name             | number | context |
            | Chakotay Marquis | 1061   | default |
        When I link user "Chakotay Marquis" with voicemail "1061@default" via RESTAPI
        Then I get a response with status "400"
        Then I get an error message matching "Invalid parameters: user with id \d+ does not have any line"

    Scenario: Link a voicemail with a user that has a SIP line
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Tuvok     | Vulcan   | 1063   | default | sip      |
        Given I have the following voicemails:
            | name            | number | context |
            | Tuvok Vulcan    | 1063   | default |
        When I link user "Tuvok Vulcan" with voicemail "1063@default" via RESTAPI
        Then I get a response with status "201"
        Then I get a response with a voicemail id
        Then I get a response with a user id
        Then I get a header with a location matching "/1.1/users/\d+/voicemail"
        Then I get a response with a link to the "voicemails" resource using the id "voicemail_id"
        Then I get a response with a link to the "users" resource using the id "user_id"

    Scenario: Link a voicemail with a user that has an SCCP line
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Tom       | Paris    | 1064   | default | sccp     |
        Given I have the following voicemails:
            | name      | number | context |
            | Tom Paris | 1064   | default |
        When I link user "Tom Paris" with voicemail "1064@default" via RESTAPI
        Then I get a response with status "201"
        Then I get a response with a voicemail id
        Then I get a response with a user id
        Then I get a header with a location matching "/1.1/users/\d+/voicemail"
        Then I get a response with a link to the "voicemails" resource using the id "voicemail_id"
        Then I get a response with a link to the "users" resource using the id "user_id"

    Scenario: Link a voicemail with a user that has a custom line
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Harry     | Kim      | 1065   | default | custom   |
        Given I have the following voicemails:
            | name      | number | context |
            | Harry Kim | 1065   | default |
        When I link user "Harry Kim" with voicemail "1065@default" via RESTAPI
        Then I get a response with status "201"
        Then I get a response with a voicemail id
        Then I get a response with a user id
        Then I get a header with a location matching "/1.1/users/\d+/voicemail"
        Then I get a response with a link to the "voicemails" resource using the id "voicemail_id"
        Then I get a response with a link to the "users" resource using the id "user_id"

    Scenario: Link a voicemail with a user that already has one
        Given there are users with infos:
            | firstname | lastname | number | context | protocol | voicemail_name  | voicemail_number |
            | B'Elanna  | Torres   | 1065   | default | sip      | B'Elanna Torres | 1065             |
        When I link user "B'Elanna Torres" with voicemail "1065@default" via RESTAPI
        Then I get a response with status "400"
        Then I get an error message matching "Invalid parameters: user with id \d+ already has a voicemail"

    Scenario: Get voicemail link when it doesn't exist
        Given there are users with infos:
            | firstname | lastname | number | context | protocol |
            | Neelix    | Talaxian | 1066   | default | sip      |
        When I request the voicemail associated to user "Neelix" "Talaxian" via RESTAPI
        Then I get a response with status "404"
        Then I get an error message matching "User with id=\d+ does not have a voicemail"

    Scenario: Get voicemail link when user has a voicemail
        Given there are users with infos:
            | firstname | lastname | number | context | protocol | voicemail_name | voicemail_number |
            | Kes       | Ocampan  | 1067   | default | sip      | Kes Ocampan    | 1067             |
        When I request the voicemail associated to user "Tuvok" "Vulcan" via RESTAPI
        Then I get a response with status "200"
        Then I get a response with a voicemail id
        Then I get a response with a user id
        Then I get a response with a link to the "voicemails" resource using the id "voicemail_id"
        Then I get a response with a link to the "users" resource using the id "user_id"

    Scenario: Get voicemail link when user does not exist
        Given there are no users with id "9999"
        When I request the voicemail associated to user with id "9999" via RESTAPI
        Then I get a response with status "404"
        Then I get an error message "User with id=9999 does not exist"
