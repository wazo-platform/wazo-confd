Feature: REST API Voicemails

    Scenario: Get a voicemail
        Given I have the following voicemails:
            | name            | number | context |
            | Jean-Luc Picard | 1000   | default |
        When I send a request for the voicemail "1000@default", using its id
        Then I get a response with status "200"
        Then I get a response with a link to the "voicemails" resource
        Then I have the following voicemails via CONFD:
            | name            | number | context | attach_audio | delete_messages | ask_password |
            | Jean-Luc Picard | 1000   | default | false        | false           | true         |

    Scenario: Get a voicemail with all parameters
        Given I have the following voicemails:
            | name          | number | context | password | email            | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | William Riker | 1001   | default | 1234     | test@example.com | en_US    | eu-fr    | 100          | true         | false           | false        |
        When I send a request for the voicemail "1001@default", using its id
        Then I get a response with status "200"
        Then I get a response with a link to the "voicemails" resource
        Then I have the following voicemails via CONFD:
            | name          | number | context | password | email            | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | William Riker | 1001   | default | 1234     | test@example.com | en_US    | eu-fr    | 100          | true         | false           | false        |

    Scenario: Voicemail list
        Given I have the following voicemails:
            | name            | number | context | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | Geordi La Forge | 1002   | default | en_US    | eu-fr    | 100          | true         | false           | true         |
            | Tasha Yar       | 1003   | default | fr_FR    | eu-fr    | 10           | false        | true            | false        |
        When I request the list of voicemails via CONFD
        Then I get a response with status "200"
        Then I get a list containing the following voicemails via CONFD:
            | name            | number | context | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | Geordi La Forge | 1002   | default | en_US    | eu-fr    | 100          | true         | false           | true         |
            | Tasha Yar       | 1003   | default | fr_FR    | eu-fr    | 10           | false        | true            | false        |

    Scenario: Creating a voicemail with required fields
        Given there is no voicemail with number "1000" and context "default"
        When I create the following voicemails via CONFD:
          | name       | number | context |
          | Joe Dahool | 1000   | default |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "voicemails" resource
        Then I get a response with a link to the "voicemails" resource
        Then I have the following voicemails via CONFD:
          | name       | number | context |
          | Joe Dahool | 1000   | default |

    Scenario: Creating a voicemail with all fields
        Given there is no voicemail with number "1000" and context "default"
        When I create the following voicemails via CONFD:
          | name       | number | context | password | email          | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
          | Joe Dahool | 1000   | default | 1234     | joe@dahool.com | fr_FR    | eu-fr    | 50           | true         | false           | false        |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "voicemails" resource
        Then I get a response with a link to the "voicemails" resource
        Then I have the following voicemails via CONFD:
          | name       | number | context | password | email          | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
          | Joe Dahool | 1000   | default | 1234     | joe@dahool.com | fr_FR    | eu-fr    | 50           | true         | false           | false        |

    Scenario: Creating two voicemails with the same number but different context
        Given there is no voicemail with number "1000" and context "default"
        Given there is no voicemail with number "1000" and context "statscenter"
        When I create the following voicemails via CONFD:
          | name       | number | context     |
          | Joe Dahool | 1000   | default     |
        Then I get a response with status "201"
        Then I have the following voicemails via CONFD:
          | name       | number | context     |
          | Joe Dahool | 1000   | default     |
        When I create the following voicemails via CONFD:
          | name       | number | context     |
          | Kim Jung   | 1000   | statscenter |
        Then I get a response with status "201"
        Then I have the following voicemails via CONFD:
          | name       | number | context     |
          | Kim Jung   | 1000   | statscenter |

    Scenario: Delete a voicemail associated to nothing
        Given I have the following voicemails:
            | name       | number | context | email                      |
            | Jadzia Dax | 1031   | default | jadzia.dax@deep.space.nine |
        When I delete voicemail "1031@default" via CONFD
        Then I get a response with status "204"
        Then voicemail with number "1031" no longer exists

    Scenario: Delete a voicemail associated to an incoming call
        Given I have the following voicemails:
            | name       | number | context |
            | Jake Sisko | 1034   | default |
        Given there is an incall "1034" in context "from-extern" to the "Voicemail" "1034@default"
        When I delete voicemail "1034@default" via CONFD
        Then I get a response with status "204"
        Then incall "1034" is associated to nothing

    Scenario: Edit a voicemail with required fields
        Given there is no voicemail with number "1000" and context "default"
        Given I have the following voicemails:
            | name       | number | context | email                      |
            | Jadzia Dax | 1598   | default | jadzia.dax@deep.space.nine |
        When I edit voicemail "1598@default" via CONFD:
            | name       | number | context |
            | Joe Dahool | 1000   | default |
        Then I get a response with status "204"
        When I send a request for the voicemail "1000@default", using its id
        Then I have the following voicemails via CONFD:
            | name       | number | context | email                      |
            | Joe Dahool | 1000   | default | jadzia.dax@deep.space.nine |

    Scenario: Edit a voicemail with all fields
        Given there is no voicemail with number "1000" and context "default"
        Given I have the following voicemails:
            | name       | number | context | password | email          | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | Super Hero | 2000   | default | 4566     | ggd@gfggdd.com | en_US    | eu-fr    | 10           | false        | true            | true         |
        When I edit voicemail "2000@default" via CONFD:
            | name       | number | context | password | email          | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | Joe Dahool | 1000   | default | 1234     | joe@dahool.com | fr_FR    | eu-fr    | 50           | true         | false           | false        |
        Then I get a response with status "204"
        When I send a request for the voicemail "1000@default", using its id
        Then I have the following voicemails via CONFD:
            | name       | number | context | password | email          | language | timezone | max_messages | attach_audio | delete_messages | ask_password |
            | Joe Dahool | 1000   | default | 1234     | joe@dahool.com | fr_FR    | eu-fr    | 50           | true         | false           | false        |

    Scenario: Edit two voicemails with the same number but different context
        Given there is no voicemail with number "1001" and context "default"
        Given there is no voicemail with number "2001" and context "statscenter"
        Given I have the following voicemails:
            | name       | number | context     |
            | Joe Dahool | 1000   | default     |
            | Joe Dahool | 2000   | statscenter |
        When I edit voicemail "1000@default" via CONFD:
            | name       | number | context     |
            | Joe Dahool | 1001   | default     |
        Then I get a response with status "204"
        When I send a request for the voicemail "1001@default", using its id
        Then I have the following voicemails via CONFD:
            | name       | number | context     |
            | Joe Dahool | 1001   | default     |
        When I edit voicemail "2000@statscenter" via CONFD:
            | name       | number | context     |
            | Kim Jung   | 2001   | statscenter |
        Then I get a response with status "204"
        When I send a request for the voicemail "2001@statscenter", using its id
        Then I have the following voicemails via CONFD:
            | name       | number | context     |
            | Kim Jung   | 2001   | statscenter |
