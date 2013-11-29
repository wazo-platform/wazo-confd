Feature: Link a line and an extension

    Scenario: Link an extension with a line that doesn't exist
        Given I have no line with id "138710"
        Given I have the following extensions:
            | exten | context |
            | 1500  | default |
        When I link extension "1500@default" with line id "138710"
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: line_id 138710 does not exist"

    Scenario: Link a line with an extension that doesn't exist
        Given I have no extension with id "292333"
        Given I have the following lines:
            | id     | context | protocol | device_slot |
            | 687078 | default | sip      | 1           |
        When I link extension id "292333" with line id "687078"
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: extension_id 292333 does not exist"

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
        When I link extension "1503@default" with line id "980133"
        Then I get a response with status "201"
        Then I get a header with a location matching "/1.1/lines/\d+/extension"
        Then I get a response with a link to the "lines" resource using the id "line_id"
        Then I get a response with a link to the "extensions" resource using the id "extension_id"

    Scenario: Link an extension to a line that already has one 
        Given I have the following extensions:
            | exten | context |
            | 1504  | default |
            | 1505  | default |
        Given I have the following lines:
            | id     | context | protocol | device_slot |
            | 841902 | default | sip      | 1           |
        When I link extension "1504@default" with line id "841902"
        Then I get a response with status "201"
        When I link extension "1505@default" with line id "841902"
        Then I get a response with status "400"
        Then I get an error message matching "Extension is already associated to a line"

    Scenario: Get the extension associated to a line that doesn't exist
        Given I have no line with id "300596"
        When I send a request for the extension associated to line id "300596"
        Then I get a response with status "404"
        Then I get an error message "Line with id=300596 does not exist"

    Scenario: Get the extension associated to a line with no extensions
        Given I have a SIP line with id "211536"
        When I send a request for the extension associated to line id "211536"
        Then I get a response with status "404"
        Then I get an error message "Line with id=211536 does not have any extension associated"

    Scenario: Get the extension associated to a line
        Given I have the following user, line and extension linked together:
            | firstname | lastname | extension | context | line id | protocol |
            | Leonard   | McCoy    | 1507      | default | 507     | sip      |
        When I request the extension associated to line id "507"
        Then I get a response with status "200"
        Then the response has a "lines" link using the id "line_id"
        Then the response has a "extensions" link using the id "extension_id"

    Scenario: Dissociate an extension from a line that doesn't exist
        Given I have no line with id "188404"
        When I dissociate the extension associated to line id "188404"
        Then I get a response with status "404"
        Then I get an error message "Line with id=188404 does not exist"

    Scenario: Dissociate an extension from a line that doesn't have one
        Given I have a SIP line with id "116775"
        When I dissociate the extension associated to line id "116775"
        Then I get a response with status "404"
        Then I get an error message "Line with id=116775 does not have an extension"

    Scenario: Dissociate an extension from the line
        Given I have the following user, line and extension linked together:
            | firstname  | lastname | extension | context | line id | protocol |
            | Montgomery | Scotty   | 1509      | default | 509     | sip      |
        When I dissociate the extension associated to line id "509"
        Then I get a response with status "204"
