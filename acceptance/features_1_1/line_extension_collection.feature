Feature: Link a line and an extension

    Scenario: List the extensions associated to a line that does not exist
        When I get the list of extensions associated to a fake line
        Then I get a response with status "404"
        Then I get an error message matching "Line with line_id=\d+ does not exist"

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
        Given extension "1665@default" is associated to SIP line "ousmane"
        Given extension "1889@from-extern" is associated to SIP line "ousmane"
        When I get the list of extensions associated to SIP line "ousmane"
        Then I get a response with status "200"
        Then I get a list with 2 of 2 items
        Then each item has a "lines" link using the id "line_id"
        Then each item has a "extensions" link using the id "extension_id"

    Scenario: Get the line associated to an extension that does not exist
        When I get the line associated to a fake extension
        Then I get a response with status "404"
        Then I get an error message matching "Extension with id=\d+ does not exist"

    Scenario: Get the line associated to an an extension with no lines associated
        Given I have the following extensions:
            | exten | context |
            | 1289  | default |
        When I get the line associated to extension "1289@default"
        Then I get a response with status "404"
        Then I get an error message matching "Extension with id=\d+ does not have a line"

    Scenario: Get the line associated to an an extension
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

    Scenario: Associate an extension with a line that does not exist
        Given I have the following extensions:
            | exten | context |
            | 1500  | default |
        When I associate the extension "1500@default" with a fake line
        Then I get a response with status "400"
        Then I get an error message matching "Nonexistent parameters: line_id \d+ does not exist"

    Scenario: Associate an extension that does not exist with a line
        Given I have the following lines:
            | username | protocol | context | device_slot |
            | cheikh   | sip      | default | 1           |
        When I associate a fake extension to SIP line "cheikh"
        Then I get a response with status "400"
        Then I get an error message matching "Nonexistent parameters: extension_id \d+ does not exist"

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
        When I associate extension "1503@default" to SIP line "william"
        Then I get a response with status "201"
        Then I get a header with a location matching "/1.1/lines/\d+/extension"
        Then I get a response with a link to the "lines" resource using the id "line_id"
        Then I get a response with a link to the "extensions" resource using the id "extension_id"

    Scenario: Associate an incoming call to a SIP line without a user
        Given I have the following lines:
            | username | protocol | context | device_slot |
            | bambara  | sip      | default | 1           |
        Given I have the following extensions:
            | exten | context     |
            | 1084  | from-extern |
        When I associate extension "1084@from-extern" to SIP line "bambara"
        Then I get a response with status "400"
        Then I get an error message matching "line is not associated with a user"

    Scenario: Associate an incoming call to a SIP line
        Given I have the following lines:
            | username | protocol | context | device_slot |
            | seitika  | sip      | default | 1           |
        Given I have the following extensions:
            | exten | context     |
            | 1229  | from-extern |
        Given I have the following users:
            | firstname | lastname |
            | Seitika   | Bambara  |
        When I associate extension "1229@from-extern" to SIP line "seitika"
        Then I get a response with status "201"
        Then I get a header with a location matching "/1.1/lines/\d+/extension"
        Then I get a response with a link to the "lines" resource using the id "line_id"
        Then I get a response with a link to the "extensions" resource using the id "extension_id"

    Scenario: Associate an extension with a SIP line already associated
        Given I have the following lines:
            | username | protocol | context | device_slot |
            | dominic  | sip      | default | 1           |
        Given I have the following extensions:
            | exten | context |
            | 1504  | default |
            | 1505  | default |
        Given I have the following users:
            | firstname | lastname |
            | Dominic   | Djembe   |
        Given SIP line "dominic" is associated to user "Dominic" "Djembe"
        Given extension "1504@default" is associated to SIP line "dominic"
        When I associate extension "1505@default" to SIP line "dominic"
        Then I get a response with status "400"
        Then I get an error message matching "Invalid parameters: line already associated with a context of type 'internal'"
