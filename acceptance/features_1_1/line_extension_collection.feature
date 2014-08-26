Feature: Link a line and an extension

    Scenario: List the extensions associated to a line with no extensions associated
        Given I have the following lines:
            | username | protocol | context | device_slot |
            | benkadi  | sip      | default | 1           |
        When I get the list of extensions associated to SIP line "benkadi"
        Then I get a response with status "200"
        Then I get an empty list

    Scenario: List one extension associated to a line
        Given I have the following lines:
            | username | protocol | context | device_slot |
            | nireli   | sip      | default | 1           |
        Given I have the following extensions:
            | exten | context |
            | 1507  | default |
        Given extension "1507@default" is associated to SIP line "nireli"
        When I get the list of extensions associated to SIP line "nireli"
        Then I get a response with status "200"
        Then I get a list with 1 of 1 items
        Then each item has a "lines" link using the id "line_id"
        Then each item has a "extensions" link using the id "extension_id"

    Scenario: List all extensions associated to a line
        Given I have the following lines:
            | username | protocol | context | device_slot |
            | ousmane  | sip      | default | 1           |
        Given I have the following extensions:
            | exten | context     |
            | 1665  | default     |
            | 1889  | from-extern |
        Given I have the following users:
            | firstname | lastname |
            | Ousmane   | Keita    |
        Given SIP line "ousmane" is associated to user "Ousmane" "Keita"
        Given extension "1665@default" is associated to SIP line "ousmane"
        Given extension "1889@from-extern" is associated to SIP line "ousmane"
        When I get the list of extensions associated to SIP line "ousmane"
        Then I get a response with status "200"
        Then I get a list with 2 of 2 items
        Then each item has a "lines" link using the id "line_id"
        Then each item has a "extensions" link using the id "extension_id"

    Scenario: Get the line associated to an extension
        Given I have the following lines:
            | username | protocol | context | device_slot |
            | boubacar | sip      | default | 1           |
        Given I have the following extensions:
            | exten | context |
            | 1282  | default |
        Given extension "1282@default" is associated to SIP line "boubacar"
        When I get the line associated to extension "1282@default"
        Then I get a response with status "200"
        Then I get a response with a link to the "lines" resource using the id "line_id"
        Then I get a response with a link to the "extensions" resource using the id "extension_id"

    Scenario: Get the line associated to an incall
        Given I have the following lines:
            | username  | protocol | context | device_slot |
            | abdoulaye | sip      | default | 1           |
        Given I have the following extensions:
            | exten | context     |
            | 1284  | default     |
            | 1284  | from-extern |
        Given I have the following users:
            | firstname | lastname |
            | Abdoulaye | Bhoye    |
        Given SIP line "abdoulaye" is associated to user "Abdoulaye" "Bhoye"
        Given extension "1284@default" is associated to SIP line "abdoulaye"
        Given extension "1284@from-extern" is associated to SIP line "abdoulaye"
        When I get the line associated to extension "1284@from-extern"
        Then I get a response with status "200"
        Then I get a response with a link to the "lines" resource using the id "line_id"
        Then I get a response with a link to the "extensions" resource using the id "extension_id"

    Scenario: Associate an extension already associated with a queue
        Given there are queues with infos:
            | name    | number | context |
            | zohkaro | 3442   | default |
        Given I have the following lines:
            | username | protocol | context | device_slot |
            | zohkaro  | sip      | default | 1           |
        When I associate extension "3442@default" to sip line "zohkaro"
        Then I get a response with status "400"
        Then I get an error message matching "Resource Error - Extension is associated with a queue"

    Scenario: Associate an extension with a SIP line
        Given I have the following lines:
            | username | protocol | context | device_slot |
            | mamadou  | sip      | default | 1           |
        Given I have the following extensions:
            | exten | context |
            | 1343  | default |
        When I associate extension "1343@default" to SIP line "mamadou"
        Then I get a response with status "201"
        Then I get a header with a location matching "/1.1/lines/\d+/extension"
        Then I get a response with a link to the "lines" resource using the id "line_id"
        Then I get a response with a link to the "extensions" resource using the id "extension_id"

    Scenario: Associate an extension with a SIP line associated to a user
        Given I have the following lines:
            | username | protocol | context | device_slot |
            | william  | sip      | default | 1           |
        Given I have the following extensions:
            | exten | context |
            | 1885  | default |
        Given I have the following users:
            | firstname | lastname |
            | William   | Shatner  |
        Given SIP line "william" is associated to user "William" "Shatner"
        When I associate extension "1885@default" to SIP line "william"
        Then I get a response with status "201"
        Then I get a header with a location matching "/1.1/lines/\d+/extension"
        Then I get a response with a link to the "lines" resource using the id "line_id"
        Then I get a response with a link to the "extensions" resource using the id "extension_id"

    Scenario: Associate an incoming call to a SIP line
        Given I have the following lines:
            | username | protocol | context | device_slot |
            | seitika  | sip      | default | 1           |
        Given there is no incall "1229" in context "from-extern"
        Given I have the following extensions:
            | exten | context     |
            | 1229  | from-extern |
        Given I have the following users:
            | firstname | lastname |
            | Seitika   | Bambara  |
        Given SIP line "seitika" is associated to user "Seitika" "Bambara"
        When I associate extension "1229@from-extern" to SIP line "seitika"
        Then I get a response with status "201"
        Then I get a header with a location matching "/1.1/lines/\d+/extension"
        Then I get a response with a link to the "lines" resource using the id "line_id"
        Then I get a response with a link to the "extensions" resource using the id "extension_id"

    Scenario: Dissociate an extension from a SIP line with a user
        Given I have the following lines:
            | username  | protocol | context | device_slot |
            | duranteau | sip      | default | 1           |
        Given I have the following extensions:
            | exten | context |
            | 1650  | default |
        Given I have the following users:
            | firstname | lastname  |
            | Mohammed  | Duranteau |
        Given SIP line "duranteau" is associated to user "Mohammed" "Duranteau"
        Given extension "1650@default" is associated to SIP line "duranteau"
        When I dissociate extension "1650@default" from SIP line "duranteau"
        Then I get a response with status "204"

    Scenario: Dissociate an extension from a line
        Given I have the following lines:
            | username | protocol | context | device_slot |
            | ibrahim  | sip      | default | 1           |
        Given I have the following extensions:
            | exten | context |
            | 1744  | default |
        Given extension "1744@default" is associated to SIP line "ibrahim"
        When I dissociate extension "1744@default" from SIP line "ibrahim"
        Then I get a response with status "204"

    Scenario: Dissociate an incoming call from a line
        Given I have the following lines:
            | username  | protocol | context | device_slot |
            | abdoulaye | sip      | default | 1           |
        Given I have the following extensions:
            | exten | context     |
            | 1510  | from-extern |
        Given I have the following users:
            | firstname | lastname  |
            | Mao       | Abdoulaye |
        Given SIP line "abdoulaye" is associated to user "Mao" "Abdoulaye"
        Given extension "1510@from-extern" is associated to SIP line "abdoulaye"
        When I dissociate extension "1510@from-extern" from SIP line "abdoulaye"
        Then I get a response with status "204"

    Scenario: Dissociate an extension from a line with a device
        Given I have the following devices:
            | ip             | mac               |
            | 192.168.167.31 | 04:7f:14:ba:9a:23 |
        Given I have the following lines:
            | username | protocol | context | device_slot |
            | moussa   | sip      | default | 1           |
        Given I have the following extensions:
            | exten | context |
            | 1401  | default |
        Given I have the following users:
            | firstname | lastname |
            | Moussa    | Oury     |
        Given SIP line "moussa" is associated to user "Moussa" "Oury"
        Given extension "1401@default" is associated to SIP line "moussa"
        Given device with ip "192.168.167.31" is provisionned with SIP line "moussa"
        When I dissociate extension "1401@default" from SIP line "moussa"
        Then I get a response with status "400"
        Then I get an error message matching "Resource Error - Line is associated with a Device"
