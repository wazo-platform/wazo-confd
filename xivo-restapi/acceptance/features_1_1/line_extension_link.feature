Feature: Link a line and an extension

    Scenario: Link an extension with a line that doesn't exist
        Given I have no line with id "500"
        Given I have the following extensions:
            | exten | context |
            | 1500  | default |
        When I link extension "1501@default" with line id "500"
        Then I get a response with status "404"
        Then I get an error message "Line with id=500 does not exist"

    Scenario: Link a line with an extension that doesn't exist
        Given I have no extension with id "9999"
        Given I have a SIP line with id "501"
        When I link extension id "9999" with line id "501"
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: extension 9999 does not exist"

    Scenario: Link an extension with a SIP line without a user
        Given I have a SIP line with id "502"
        Given I have the following extensions:
            | exten | context |
            | 1502  | default |
        When I link extension "1502@default" with line id "502"
        Then I get a response with status "400"
        Then I get an error message "Line 502 does not have any user associated"

    Scenario: Link an extension with a SIP line
        Given there are users with infos:
            | firstname | lastname |
            | William   | Shatner  |
        Given I have the following extensions:
            | exten | context |
            | 1503  | default |
        Given I have a SIP line with id "503"
        Given line "503" is linked with user "William" "Shatner"
        When I link extension "1503@default" with line id "503"
        Then I get a response with status "201"
        Then I get a response with a line id
        Then I get a response with an extension id
        Then I get a header with a location matching "/1.1/lines/\d+/extension"
        Then I get a response with a link to the "lines_sip" resource using the id "line_id"
        Then I get a response with a link to the "extensions" resource using the id "extension_id"

    Scenario: Link an extension to a line that already has one 
        Given I have the following user, line and extension linked together:
            | firstname | lastname | extension | context | line id | protocol |
            | Commander | Spock    | 1504      | default | 504     | sip      |
        When I link extension "1505@default" with the line of user "Commander" "Spock"
        Then I get a response with status "400"
        Then I get an error message matching "Extension is already associated to a line"

    Scenario: Get the extension associated to a line that doesn't exist
        Given I have no line with id "505"
        When I send a request for the extension associated to line id "505"
        Then I get a response with status "404"
        Then I get an error message "Line with id=505 does not exist"

    Scenario: Get the extension associated to a line with no extensions
        Given I have a SIP line with id "506"
        When I send a request for the extension associated to line id "506"
        Then I get a response with status "404"
        Then I get an error message "Line 506 does not have any extension associated"

    Scenario: Get the extension associated to a line
        Given I have the following user, line and extension linked together:
            | firstname | lastname | extension | context | line id | protocol |
            | Leonard   | McCoy    | 1507      | default | 507     | sip      |
        When I request the extension associated to line id "507"
        Then I get a response with status "200"
        Then I get a response with a line id
        Then I get a response with an extension id
        Then I get a response with a link to the "lines_sip" resource using the id "line_id"
        Then I get a response with a link to the "extensions" resource using the id "extension_id"

    Scenario: Dissociate an extension from a line that doesn't exist
        Given I have no line with id "9999"
        When I dissociate the extension associated to line id "9999"
        Then I get a response with status "404"
        Then I get an error message "Line with id=9999 does not exist"

    Scenario: Dissociate an extension from a line that doesn't have one
        Given I have a SIP line with id "508"
        When I dissociate the extension associated to line id "508"
        Then I get a response with status "404"
        Then I get an error message "Line does not have an extension"

    Scenario: Dissociate an extension from the line
        Given I have the following user, line and extension linked together:
            | firstname  | lastname | extension | context | line id | protocol |
            | Montgomery | Scotty   | 1509      | default | 509     | sip      |
        When I dissociate the extension associated to line id "509"
        Then I get a response with status "204"
