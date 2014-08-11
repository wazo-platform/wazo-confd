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

    Scenario: Filter extension by type
        Given I have the following extensions:
            | exten | context     |
            | 1036  | default     |
            | 1936  | from-extern |

        When I access the list of extensions using the following parameters:
            | name | value    |
            | type | internal |
        Then I get a response with status "200"
        Then I get a list containing the following extensions:
            | exten | context |
            | 1036  | default |
        Then I get a list that does not contain the following extensions:
            | exten | context     |
            | 1936  | from-extern |

        When I access the list of extensions using the following parameters:
            | name | value  |
            | type | incall |
        Then I get a response with status "200"
        Then I get a list containing the following extensions:
            | exten | context     |
            | 1936  | from-extern |
        Then I get a list that does not contain the following extensions:
            | exten | context |
            | 1036  | default |

    Scenario: Get an extension
        Given I have the following extensions:
            | id     | exten | context |
            | 447614 | 1599  | default |
        When I access the extension with id "447614"
        Then I get a response with status "200"
        Then I have an extension with the following parameters:
            | id     | exten | context |
            | 447614 | 1599  | default |

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

    Scenario: Creating an extenion in incall range with DID length
        Given there are contexts with infos:
            | type   | name   | range_start | range_end  | entity_name | didlength |
            | incall | quebec | 4185550000  | 4185559999 | xivo_entity | 4         |
        Given I have no extension with exten "1111@quebec"
        When I create an extension with the following parameters:
            | exten | context |
            | 1111  | quebec  |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "extensions" resource
        Then I get a response with a link to the "extensions" resource

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

    Scenario: Editing the exten of a extension
        Given I have no extension with exten "1145@default"
        Given I have the following extensions:
          | id     | exten | context |
          | 113444 | 1045  | default |
        When I update the extension with id "113444" using the following parameters:
          | exten |
          | 1145  |
        Then I get a response with status "204"
        When I access the extension with id "113444"
        Then I have an extension with the following parameters:
          | id     | exten | context |
          | 113444 | 1145  | default |

    Scenario: Editing the context of a extension
        Given I have no extension with exten "1833@toto"
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
        When I access the extension with id "214489"
        Then I have an extension with the following parameters:
          | id     | exten | context |
          | 214489 | 1833  | toto    |

    Scenario: Editing the exten, context of a extension
        Given I have no extension with exten "1996@patate"
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
        When I access the extension with id "113469"
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
        When I access the extension with id "962441"
        Then I have an extension with the following parameters:
          | id     | exten | context | commented |
          | 962441 | 1107  | default | false     |

    Scenario: Delete an extension
        Given I have the following extensions:
            | id     | exten | context |
            | 954147 | 1846  | default |
        When I delete extension with id "954147"
        Then I get a response with status "204"
        Then the extension "954147" no longer exists

    Scenario: Delete an extension associated to a line
        Given I have the following lines:
            | id     | context | protocol | device_slot |
            | 299568 | default | sip      | 1           |
        Given I have the following extensions:
            | id     | exten | context |
            | 328785 | 1226  | default |
        Given line "299568" is linked with extension "1226@default"
        When I delete extension with id "328785"
        Then I get a response with status "400"
        Then I get an error message matching "Resource Error - Extension is associated with a Line"

    Scenario: Delete an extension associated to a queue
        Given there are queues with infos:
            | name     | number | context |
            | ex-queue | 3198   | default |
        When I delete extension "3198@default"
        Then I get a response with status "400"
        Then I get an error message matching "Resource Error - Extension is associated with a queue"
