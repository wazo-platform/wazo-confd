Feature: Link a line and an extension

    Scenario: Link an extension with a SIP line without a user
        Given I have the following lines:
            | id     | context | protocol | device_slot |
            | 340940 | default | sip      | 1           |
        Given I have the following extensions:
            | exten | context |
            | 1502  | default |
        When I link extension "1502@default" with line id "340940"
        Then I get a response with status "201"
        Then I get a header with a location matching "/1.1/lines/\d+/extension"
        Then I get a response with a link to the "lines" resource using the id "line_id"
        Then I get a response with a link to the "extensions" resource using the id "extension_id"

    Scenario: Link an extension with a SIP line associated to a user
        Given there are users with infos:
            | firstname | lastname |
            | William   | Shatner  |
        Given I have the following extensions:
            | exten | context |
            | 1503  | default |
        Given I have the following lines:
            | id     | context | protocol | device_slot |
            | 980133 | default | sip      | 1           |
        Given line "980133" is linked with user "William" "Shatner"
        Given line "980133" is linked with extension "1503@default"
        Then I get a header with a location matching "/1.1/lines/\d+/extension"
        Then I get a response with a link to the "lines" resource using the id "line_id"
        Then I get a response with a link to the "extensions" resource using the id "extension_id"

    Scenario: Get the extension associated to a line
        Given there are users with infos:
            | firstname | lastname |
            | Leonard   | McCoy    |
        Given I have the following extensions:
            | exten | context |
            | 1507  | default |
        Given I have the following lines:
            | id     | context | protocol | device_slot |
            | 835437 | default | sip      | 1           |
        Given line "835437" is linked with user "Leonard" "McCoy"
        Given line "835437" is linked with extension "1507@default"
        When I send a request for the extension associated to line id "835437"
        Then I get a response with status "200"
        Then I get a response with a link to the "lines" resource using the id "line_id"
        Then I get a response with a link to the "extensions" resource using the id "extension_id"

    Scenario: Get the line associated to an extension
        Given I have the following extensions:
            | exten | context |
            | 1749  | default |
        Given I have the following lines:
            | id     | context | protocol | device_slot |
            | 835437 | default | sip      | 1           |
        Given line "835437" is linked with extension "1749@default"
        When I send a request for the line associated to extension with exten "1749@default"
        Then I get a response with status "200"
        Then I get a response with a link to the "lines" resource using the id "line_id"
        Then I get a response with a link to the "extensions" resource using the id "extension_id"

    Scenario: Dissociate an extension from a line with a user
        Given there are users with infos:
            | firstname  | lastname |
            | Montgomery | Scott    |
        Given I have the following extensions:
            | exten | context |
            | 1509  | default |
        Given I have the following lines:
            | id     | context | protocol | device_slot |
            | 834043 | default | sip      | 1           |
        Given line "834043" is linked with user "Montgomery" "Scott"
        Given line "834043" is linked with extension "1509@default"
        When I dissociate the extension associated to line id "834043"
        Then I get a response with status "204"

    Scenario: Dissociate an extension from a line
        Given I have the following extensions:
            | exten | context |
            | 1510  | default |
        Given I have the following lines:
            | id     | context | protocol | device_slot |
            | 832642 | default | sip      | 1           |
        Given line "832642" is linked with extension "1510@default"
        When I dissociate the extension associated to line id "832642"
        Then I get a response with status "204"

    Scenario: Dissociate an extension when a device is associated
        Given I have the following devices:
          | id                               | ip             | mac               |
          | 48ff0fbd3a53ad329ca4f248331b72ca | 192.168.167.31 | 04:7f:14:ba:9a:23 |
        Given I have the following lines:
            | id     | context | protocol | username | secret   | device_slot | device_id                        |
            | 719454 | default | sip      | a84nfkj6 | 8vbk3e7w | 1           | 48ff0fbd3a53ad329ca4f248331b72ca |
        Given I have the following extensions:
            | exten | context |
            | 1511  | default |
        Given line "719454" is linked with extension "1511@default"
        When I dissociate the extension associated to line id "719454"
        Then I get a response with status "400"
        Then I get an error message matching "Resource Error - Line is associated with a Device"
