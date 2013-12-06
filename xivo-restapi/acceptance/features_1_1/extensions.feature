Feature: REST API Extensions

    Scenario: Extension list with one extension
        Given I have the following extensions:
            | exten | context |
            | 1523  | default |
        When I access the list of extensions
        Then I get a list containing the following extensions:
            | exten | context |
            | 1523  | default |

    Scenario: Extension list with two extensions
        Given I have the following extensions:
            | exten | context |
            | 1983  | default |
            | 1947  | default |
        When I access the list of extensions
        Then I get a list containing the following extensions:
            | exten | context |
            | 1983  | default |
            | 1947  | default |

    Scenario: User link list by extension_id with no link
        Given I have no extension with id "965734"
        When I ask for the list of user_links with extension_id "965734"
        Then I get a response with status "200"
        Then I get an empty list

    Scenario: User link list by extension_id with 1 user
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 995476 | Greg      | Sanderson |
        Given I only have the following lines:
            |     id | context | protocol | device_slot |
            | 124689 | default | sip      |           1 |
        Given I have the following extensions:
            | id     | context | exten |
            | 995473 | default | 1775  |
        Given the following users, lines, extensions are linked:
            | user_id | line_id | extension_id |
            | 995476  | 124689  | 995473       |
        When I ask for the list of user_links with extension_id "995473"
        Then I get a response with status "200"
        Then I get the user_links with the following parameters:
            | user_id | line_id | extension_id |
            | 995476  | 124689  | 995473       |

    Scenario: User link list by extension_id with 2 users
        Given I only have the following users:
            | id     | firstname | lastname  |
            | 132449 | Greg      | Sanderson |
            | 995441 | Cedric    | Abunar    |
        Given I only have the following lines:
            |     id | context | protocol | device_slot |
            | 446168 | default | sip      |           1 |
        Given I have the following extensions:
            | id     | context | exten |
            | 995134 | default | 1358  |
        Given the following users, lines, extensions are linked:
            | user_id | line_id | extension_id |
            | 132449  | 446168  | 995134       |
            | 995441  | 446168  | 995134       |
        When I ask for the list of user_links with extension_id "995134"
        Then I get a response with status "200"
        Then I get the user_links with the following parameters:
            | user_id | line_id | extension_id |
            | 132449  | 446168  | 995134       |
            | 995441  | 446168  | 995134       |

    Scenario: Get an extension that does not exist
        Given I have no extension with id "699324"
        When I access the extension with id "699324"
        Then I get a response with status "404"

    Scenario: Get an extension
        Given I have the following extensions:
            | id     | exten | context |
            | 447614 | 1599  | default |
        When I access the extension with id "447614"
        Then I get a response with status "200"
        Then I have an extension with the following parameters:
            | id     | exten | context |
            | 447614 | 1599  | default |

    Scenario: Creating an empty extension
        When I create an empty extension
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: exten,context"

    Scenario: Creating an extension with an empty number
        When I create an extension with the following parameters:
            | exten | context |
            |       | default |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: Exten required"

    Scenario: Creating an extension with an empty context
        When I create an extension with the following parameters:
            | exten | context |
            | 1000  |         |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: Context required"

    Scenario: Creating an extension with only the number
        When I create an extension with the following parameters:
            | exten |
            | 1000  |
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: context"

    Scenario: Creating an extension with only the context
        When I create an extension with the following parameters:
            | context |
            | default |
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: exten"

    Scenario: Creating an extension with invalid parameters
        When I create an extension with the following parameters:
            | toto |
            | tata |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: toto"

    Scenario: Creating a commented extension
        Given I have no extension with exten "1883@default"
        When I create an extension with the following parameters:
            | exten | context | commented |
            | 1883  | default | true      |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "extensions" resource
        Then I get a response with a link to the "extensions" resource

    Scenario: Creating an extension that isn't commented
        Given I have no extension with exten "1294@default"
        When I create an extension with the following parameters:
            | exten | context | commented |
            | 1294  | default | false     |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "extensions" resource
        Then I get a response with a link to the "extensions" resource

    Scenario: Creating an extension in user range
        Given I have no extension with exten "1000@default"
        When I create an extension with the following parameters:
            | exten | context |
            | 1000  | default |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "extensions" resource
        Then I get a response with a link to the "extensions" resource

    Scenario: Creating an extension in group range
        Given I have no extension with exten "2000@default"
        When I create an extension with the following parameters:
            | exten | context |
            | 2000  | default |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "extensions" resource
        Then I get a response with a link to the "extensions" resource

    Scenario: Creating an extension in queue range
        Given I have no extension with exten "3000@default"
        When I create an extension with the following parameters:
            | exten | context |
            | 3000  | default |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "extensions" resource
        Then I get a response with a link to the "extensions" resource

    Scenario: Creating an extension in conference room range
        Given I have no extension with exten "4000@default"
        When I create an extension with the following parameters:
            | exten | context |
            | 4000  | default |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "extensions" resource
        Then I get a response with a link to the "extensions" resource

    Scenario: Creating an extension in incall range
        Given I have no extension with exten "3954@from-extern"
        When I create an extension with the following parameters:
            | exten | context     |
            |  3954 | from-extern |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "extensions" resource
        Then I get a response with a link to the "extensions" resource

    Scenario: Creating an alphanumeric extension
        When I create an extension with the following parameters:
            | exten  | context |
            | ABC123 | default |
        Then I get a response with status "400"
        Then i get an error message "Invalid parameters: Alphanumeric extensions are not supported"

    Scenario: Creating twice the same extension
        Given I have no extension with exten "1454@default"
        When I create an extension with the following parameters:
            | exten | context |
            | 1454  | default |
        Then I get a response with status "201"
        When I create an extension with the following parameters:
            | exten | context |
            | 1454  | default |
        Then I get a response with status "400"
        Then I get an error message "Extension 1454@default already exists"

    Scenario: Creating two extensions in different contexts
        Given I have no extension with exten "1119@default"
        Given I have no extension with exten "1119@from-extern"
        When I create an extension with the following parameters:
            | exten | context |
            | 1119  | default |
        Then I get a response with status "201"
        When I create an extension with the following parameters:
            | exten | context     |
            | 1119  | from-extern |
        Then I get a response with status "201"

    Scenario: Creating an extension with a context that doesn't exist
        When I create an extension with the following parameters:
            | exten | context             |
            | 1000  | mysuperdupercontext |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: context mysuperdupercontext does not exist"

    Scenario: Creating an extension outside of context range
        When I create an extension with the following parameters:
            | exten | context |
            | 99999 | default |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: exten 99999 not inside range of context default"

    Scenario: Editing an extension that doesn't exist
        Given I have no extension with id "9999"
        When I update the extension with id "9999" using the following parameters:
          | exten |
          | 1001  |
        Then I get a response with status "404"

    Scenario: Editing an extension with parameters that don't exist
        Given I have the following extensions:
          | id     | exten | context |
          | 449721 | 1358  | default |
        When I update the extension with id "449721" using the following parameters:
          | unexisting_field |
          | unexisting value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Editing the exten of a extension
        Given I have the following extensions:
          | id     | exten | context |
          | 113444 | 1045  | default |
        When I update the extension with id "113444" using the following parameters:
          | exten |
          | 1145  |
        Then I get a response with status "204"
        When I ask for the extension with id "113444"
        Then I have an extension with the following parameters:
          | id     | exten | context |
          | 113444 | 1145  | default |

    Scenario: Editing an extension with an exten outside of context range
        Given I have the following extensions:
          | id     | exten | context |
          | 443166 | 1453  | default |
        When I update the extension with id "443166" using the following parameters:
          | exten |
          | 9999  |
      Then I get a response with status "400"
      Then I get an error message "Invalid parameters: exten 9999 not inside range of context default"

    Scenario: Editing the context of a extension
        Given I have the following extensions:
          | id     | exten | context |
          | 214489 | 1833  | default |
        Given I have the following context:
          | name | numberbeg | numberend |
          | toto | 1000      | 1999      |
        When I update the extension with id "214489" using the following parameters:
          | context |
          | toto    |
        Then I get a response with status "204"
        When I ask for the extension with id "214489"
        Then I have an extension with the following parameters:
          | id     | exten | context |
          | 214489 | 1833  | toto    |

    Scenario: Editing the extension with a context that doesn't exist
        Given I have the following extensions:
          | id     | exten | context |
          | 959476 | 1665  | default |
        When I update the extension with id "959476" using the following parameters:
          | context             |
          | mysuperdupercontext |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: context mysuperdupercontext does not exist"

    Scenario: Editing the exten, context of a extension
        Given I have the following extensions:
          | id     | exten | context |
          | 113469 | 1292  | default |
        Given I have the following context:
          | name   | numberbeg | numberend |
          | patate | 1000      | 1999      |
        When I update the extension with id "113469" using the following parameters:
          | exten | context |
          | 1996  | patate  |
        Then I get a response with status "204"
        When I ask for the extension with id "113469"
        Then I have an extension with the following parameters:
          | id     | exten | context |
          | 113469 | 1996  | patate  |

    Scenario: Editing a commented extension
        Given I have the following extensions:
          | id     | exten | context | commented |
          | 962441 | 1107  | default | true      |
        When I update the extension with id "962441" using the following parameters:
          | commented |
          | false     |
        Then I get a response with status "204"
        When I ask for the extension with id "962441"
        Then I have an extension with the following parameters:
          | id     | exten | context | commented |
          | 962441 | 1107  | default | false     |

    Scenario: Delete an extension that doesn't exist
        Given I have no extension with id "892476"
        When I delete extension "892476"
        Then I get a response with status "404"

    Scenario: Delete an extension
        Given I have the following extensions:
            | id     | exten | context |
            | 954147 | 1846  | default |
        When I delete extension "954147"
        Then I get a response with status "204"
        Then the extension "954147" no longer exists

    Scenario: Delete an extension still has a link
        Given I only have the following users:
            |     id | firstname | lastname |
            | 954471 | Clémence  | Dupond   |
        Given I only have the following lines:
            |     id | context | protocol | device_slot |
            | 996547 | default | sip      |           1 |
        Given I have the following extensions:
            | id     | context | exten |
            | 695447 | default | 1409  |
        When I create the following links:
            | user_id | line_id | extension_id | main_line |
            | 954471  | 996547  | 695447       | True      |
        Then I get a response with status "201"

        When I delete extension "695447"
        Then I get a response with status "400"
        Then I get an error message "Error while deleting Extension: extension still has a link"
