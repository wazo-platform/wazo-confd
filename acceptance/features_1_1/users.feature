Feature: REST API Users

    Scenario: User list with one user
        Given I have the following users:
          | firstname | lastname |
          | Clémence  | Dupond   |
        When I ask for the list of users
        Then I get a list containing the following users:
          | firstname | lastname | userfield | caller_id         |
          | Clémence  | Dupond   |           | "Clémence Dupond" |

    Scenario: User list with two users
        Given I have the following users:
          | firstname | lastname |
          | Clémence  | Dupond   |
          | Louis     | Martin   |
        When I ask for the list of users
        Then I get a list containing the following users:
          | firstname | lastname | userfield | caller_id         |
          | Clémence  | Dupond   |           | "Clémence Dupond" |
          | Louis     | Martin   |           | "Louis Martin"    |

    Scenario: User list ordered by lastname, then firstname
        Given I have the following users:
          | firstname | lastname |
          | Clémence  | Dupond   |
          | Louis     | Martin   |
          | Albert    | Dupond   |
          | Frédéric  | Martin   |
        When I ask for the list of users
        Then I get a list containing the following users:
          | firstname | lastname | userfield | caller_id         |
          | Albert    | Dupond   |           | "Albert Dupond"   |
          | Clémence  | Dupond   |           | "Clémence Dupond" |
          | Frédéric  | Martin   |           | "Frédéric Martin" |
          | Louis     | Martin   |           | "Louis Martin"    |

    Scenario: User search with an empty filter
        Given I have the following users:
          | firstname | lastname |
          | George    | Lucas    |
        When I search for the user ""
        Then I get a list containing the following users:
         | firstname | lastname | caller_id      |
         | George    | Lucas    | "George Lucas" |

    Scenario: User search with a filter that returns nothing
        Given I have the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "6kmsdRxV"
        Then I get an empty list
        When I search for the user "u5L3riyk"
        Then I get an empty list

    Scenario: User search using the firstname
        Given I have the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "and"
        Then I get a list containing the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "reï"
        Then I get a list containing the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "andreii"
        Then I get an empty list

    Scenario: User search using the lastname
        Given I have the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "lie"
        Then I get a list containing the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "bél"
        Then I get a list containing the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "belou"
        Then I get an empty list

    Scenario: User search using the firstname and lastname
        Given I have the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "andreï"
        Then I get a list containing the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "bélier"
        Then I get a list containing the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "reï bél"
        Then I get a list containing the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "rei bel"
        Then I get an empty list

    Scenario: User search with 2 users
        Given I have the following users:
          | firstname | lastname |
          | Remy      | Licorne  |
          | Andreï    | Bélier   |
        When I search for the user "re"
        Then I get a list containing the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
          | Remy      | Licorne  |
        When I search for the user "lic"
        Then I get a list containing the following users:
          | firstname | lastname |
          | Remy      | Licorne  |

    Scenario: Getting a user that exists
        Given I have the following users:
          | id     | firstname | lastname |
          | 323450 | Irène     | Dupont   |
        When I ask for the user with id "323450"
        Then I get a response with status "200"
        Then I get a user with the following parameters:
          | id     | firstname | lastname | userfield |
          | 323450 | Irène     | Dupont   |           |

    Scenario: Getting a user with all available parameters:
        Given I have the following users:
            | id     | firstname | lastname | timezone         | language | description        | caller_id | outgoing_caller_id | mobile_phone_number | username | password | music_on_hold | preprocess_subroutine | userfield |
            | 766763 | James     | Hetfield | America/Montreal | en_US    | Metallica Musician | METAL     | anonymous          | 5551234567          | james    | hetfield | missing       | subroutine            | userfield |
        When I ask for the user with id "766763"
        Then I get a response with status "200"
        Then I get a user with the following parameters:
            | id     | firstname | lastname | timezone         | language | description        | caller_id | outgoing_caller_id | mobile_phone_number | username | password | music_on_hold | preprocess_subroutine | userfield |
            | 766763 | James     | Hetfield | America/Montreal | en_US    | Metallica Musician | "METAL"   | anonymous          | 5551234567          | james    | hetfield | missing       | subroutine            | userfield |

    Scenario: Creating a user with a valid mobile_phone_number
        When I create users with the following parameters:
            | firstname | mobile_phone_number |
            | Joe       | 5551234567          |
        Then I get a response with status "201"
        Then the created user has the following parameters:
            | firstname | mobile_phone_number |
            | Joe       | 5551234567          |

    Scenario: Creating a user with an international mobile_phone_number
        When I create users with the following parameters:
            | firstname | mobile_phone_number  |
            | Joe       | +011224563958*78#445 |
        Then I get a response with status "201"
        Then the created user has the following parameters:
            | firstname | mobile_phone_number  |
            | Joe       | +011224563958*78#445 |

    Scenario: Creating a user with a firstname
        When I create users with the following parameters:
          | firstname |
          | Irène     |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "users" resource
        Then I get a response with a link to the "users" resource
        Then the created user has the following parameters:
         | firstname | lastname | userfield | caller_id |
         | Irène     |          |           | "Irène "  |

    Scenario: Creating two users with the same firstname
        When I create users with the following parameters:
          | firstname |
          | Lord      |
          | Lord      |
        When I ask for the list of users
        Then I get a list containing the following users:
          | firstname | lastname | userfield | caller_id |
          | Lord      |          |           | "Lord "   |
          | Lord      |          |           | "Lord "   |

    Scenario: Creating a user with all available parameters
        When I create users with the following parameters:
            | firstname | lastname | timezone         | language | description        | caller_id | outgoing_caller_id | mobile_phone_number | username | password | music_on_hold | preprocess_subroutine | userfield |
            | James     | Hetfield | America/Montreal | en_US    | Metallica Musician | METAL     | anonymous          | 5551234567          | james    | hetfield | missing       | subroutine            | userfield |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "users" resource
        Then I get a response with a link to the "users" resource
        Then the created user has the following parameters:
            | firstname | lastname | timezone         | language | description        | caller_id | outgoing_caller_id | mobile_phone_number | username | password | music_on_hold | preprocess_subroutine | userfield |
            | James     | Hetfield | America/Montreal | en_US    | Metallica Musician | "METAL"   | anonymous          | 5551234567          | james    | hetfield | missing       | subroutine            | userfield |

    Scenario: Editing the firstname of a user
        Given I have the following users:
          | id     | firstname | lastname |
          | 995414 | Clémence  | Dupond   |
        When I update the user with id "995414" using the following parameters:
          | firstname |
          | Brézé     |
        Then I get a response with status "204"
        When I ask for the user with id "995414"
        Then I get a user with the following parameters:
          | id     | firstname | lastname | userfield | caller_id      |
          | 995414 | Brézé     | Dupond   |           | "Brézé Dupond" |

    Scenario: Editing the lastname of a user
        Given I have the following users:
          | id     | firstname | lastname |
          | 924465 | Clémence  | Dupond   |
        When I update the user with id "924465" using the following parameters:
          | lastname      |
          | Argentine     |
        Then I get a response with status "204"
        When I ask for the user with id "924465"
        Then I get a user with the following parameters:
          | id     | firstname | lastname  | userfield | caller_id            |
          | 924465 | Clémence  | Argentine |           | "Clémence Argentine" |

    Scenario: Editing a user associated with a voicemail
        Given there are users with infos:
            | firstname | lastname  | number | context | protocol | voicemail_name     | voicemail_number |
            | Francois  | Andouille | 1100   | default | sip      | Francois Andouille | 1100             |
        When I update user "Francois" "Andouille" with the following parameters:
            | firstname | lastname |
            | Pizza     | Poulet   |
        Then I get a response with status "204"
        When I send a request for the voicemail "1100@default", using its id
        Then I have the following voicemails via RESTAPI:
            | name         | number |
            | Pizza Poulet | 1100   |

    Scenario: Editing the firstname, lastname and caller_id of a user
        Given I have the following users:
            | id     | firstname | lastname |
            | 726313 | Clémence  | Dujas    |
        When I update the user with id "726313" using the following parameters:
            | firstname | lastname       | caller_id         |
            | Olivia    | Schtroumpfette | La Schtroumpfette |
        Then I get a response with status "204"
        When I ask for the user with id "726313"
        Then I get a user with the following parameters:
            | id     | firstname | lastname       | caller_id           |
            | 726313 | Olivia    | Schtroumpfette | "La Schtroumpfette" |

    Scenario: Editing only the caller_id of a user
        Given I have the following users:
            | id     | firstname | lastname |
            | 447520 | Benoit    | Thierri  |
        When I update the user with id "447520" using the following parameters:
            | caller_id        |
            | Grand Schtroumpf |
        Then I get a response with status "204"
        When I ask for the user with id "447520"
        Then I get a user with the following parameters:
            | id     | firstname | lastname | caller_id          |
            | 447520 | Benoit    | Thierri  | "Grand Schtroumpf" |

    Scenario: Editing all available parameters of a user
        Given I have the following users:
            | id     | firstname | lastname | timezone         | language | description        | caller_id | outgoing_caller_id | mobile_phone_number | username | password | music_on_hold | preprocess_subroutine | userfield |
            | 140270 | James     | Hetfield | America/Montreal | en_US    | Metallica Musician | METAL     | anonymous          | 5551234567          | james    | hetfield | missing       | subroutine            | userfield |
        When I update the user with id "140270" using the following parameters:
            | firstname | lastname | timezone       | language | description | caller_id | outgoing_caller_id | mobile_phone_number | username  | password | music_on_hold | preprocess_subroutine | userfield |
            | Alexander | Powell   | Africa/Abidjan | fr_FR    | updated     | ALEXANDER | default            | 1234567890          | alexander | powell   | default       | other_subroutine      | myvalue   |
        Then I get a response with status "204"
        When I ask for the user with id "140270"
        Then I get a user with the following parameters:
            | id     | firstname | lastname | timezone       | language | description | caller_id   | outgoing_caller_id | mobile_phone_number | username  | password | music_on_hold | preprocess_subroutine | userfield |
            | 140270 | Alexander | Powell   | Africa/Abidjan | fr_FR    | updated     | "ALEXANDER" | default            | 1234567890          | alexander | powell   | default       | other_subroutine      | myvalue   |

    Scenario: Deleting a user
        Given I have the following users:
          | id     | firstname | lastname |
          | 955135 | Clémence  | Dupond   |
        When I delete the user with id "955135"
        Then I get a response with status "204"
        Then the user with id "955135" no longer exists
