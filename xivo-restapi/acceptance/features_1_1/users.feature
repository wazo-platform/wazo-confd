Feature: REST API Users

    Scenario: User list with no users
        Given I have no users
        When I ask for the list of users
        Then I get an empty list

    Scenario: User list with one user
        Given I only have the following users:
          | firstname | lastname |
          | Clémence  | Dupond   |
        When I ask for the list of users
        Then I get a list with the following users:
          | firstname | lastname | userfield | caller_id         |
          | Clémence  | Dupond   |           | "Clémence Dupond" |

    Scenario: User list with two users
        Given I only have the following users:
          | firstname | lastname |
          | Clémence  | Dupond   |
          | Louis     | Martin   |
        When I ask for the list of users
        Then I get a list with the following users:
          | firstname | lastname | userfield | caller_id         |
          | Clémence  | Dupond   |           | "Clémence Dupond" |
          | Louis     | Martin   |           | "Louis Martin"    |

    Scenario: User list ordered by lastname, then firstname
        Given I only have the following users:
          | firstname | lastname |
          | Clémence  | Dupond   |
          | Louis     | Martin   |
          | Albert    | Dupond   |
          | Frédéric  | Martin   |
        When I ask for the list of users
        Then I get a list with the following users:
          | firstname | lastname | userfield | caller_id         |
          | Albert    | Dupond   |           | "Albert Dupond"   |
          | Clémence  | Dupond   |           | "Clémence Dupond" |
          | Frédéric  | Martin   |           | "Frédéric Martin" |
          | Louis     | Martin   |           | "Louis Martin"    |

    Scenario: User search with no users
        Given I have no users
        When I search for the user "Bob"
        Then I get an empty list

    Scenario: User search with an empty filter
        Given I only have the following users:
          | firstname | lastname |
          | George    | Lucas    |
        When I search for the user ""
        Then I get a list with the following users:
         | firstname | lastname | caller_id      |
         | George    | Lucas    | "George Lucas" |

    Scenario: User search with a filter that returns nothing
        Given I only have the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "bob"
        Then I get an empty list
        When I search for the user "rei"
        Then I get an empty list

    Scenario: User search using the firstname
        Given I only have the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "and"
        Then I get a list with the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "reï"
        Then I get a list with the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "andou"
        Then I get an empty list

    Scenario: User search using the lastname
        Given I only have the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "lie"
        Then I get a list with the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "bél"
        Then I get a list with the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "belou"
        Then I get an empty list

    Scenario: User search using the firstname and lastname
        Given I only have the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "andreï"
        Then I get a list with the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "bélier"
        Then I get a list with the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "reï bél"
        Then I get a list with the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "rei bel"
        Then I get an empty list

    Scenario: User search with 2 users
        Given I only have the following users:
          | firstname | lastname |
          | Remy      | Licorne  |
          | Andreï    | Bélier   |
        When I search for the user "re"
        Then I get a list with the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
          | Remy      | Licorne  |
        When I search for the user "lic"
        Then I get a list with the following users:
          | firstname | lastname |
          | Remy      | Licorne  |

    Scenario: Getting a user that doesn't exist
        Given I have no users
        When I ask for the user with id "1"
        Then I get a response with status "404"

    Scenario: Getting a user that exists
        Given I only have the following users:
          | id | firstname | lastname |
          | 1  | Irène     | Dupont   |
        When I ask for the user with id "1"
        Then I get a response with status "200"
        Then I get a user with the following parameters:
          | id | firstname | lastname | userfield |
          | 1  | Irène     | Dupont   |           |

    Scenario: Getting a user with all available parameters:
        Given I only have the following users:
            | id | firstname | lastname | timezone         | language | description        | caller_id | outgoing_caller_id | mobile_phone_number | username | password | music_on_hold | preprocess_subroutine | userfield |
            | 1  | James     | Hetfield | America/Montreal | en_US    | Metallica Musician | METAL     | anonymous          | 5551234567          | james    | hetfield | missing       | subroutine            | userfield |
        When I ask for the user with id "1"
        Then I get a response with status "200"
        Then I get a user with the following parameters:
            | id | firstname | lastname | timezone         | language | description        | caller_id | outgoing_caller_id | mobile_phone_number | username | password | music_on_hold | preprocess_subroutine | userfield |
            | 1  | James     | Hetfield | America/Montreal | en_US    | Metallica Musician | "METAL"   | anonymous          | 5551234567          | james    | hetfield | missing       | subroutine            | userfield |

    Scenario: Creating an empty user
        Given I have no users
        When I create an empty user
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: firstname"

    Scenario: Creating a user with paramters that don't exist
        Given I have no users
        When I create users with the following parameters:
          | unexisting_field |
          | unexisting_value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Creating a user with a firstname and parameters that don't exist
        Given I have no users
        When I create users with the following parameters:
          | firstname | unexisting_field |
          | Joe       | unexisting_value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Creating a user with a invalid password
        Given I have no users
        When I create users with the following parameters:
          | firstname | password |
          | Joe       | 123      |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: password"

    Scenario: Creating a user with a invalid mobile_phone_number
        Given I have no users
        When I create users with the following parameters:
          | firstname | mobile_phone_number |
          | Joe       | mobile_phone_number |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: mobile_phone_number"

    Scenario: Creating a user with a firstname
        Given I have no users
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
        Given I have no users
        When I create users with the following parameters:
          | firstname |
          | Lord      |
          | Lord      |
        When I ask for the list of users
        Then I get a list with the following users:
          | firstname | lastname | userfield | caller_id |
          | Lord      |          |           | "Lord "   |
          | Lord      |          |           | "Lord "   |

    Scenario: Creating a user with all available parameters
        Given I have no users
        When I create users with the following parameters:
            | id | firstname | lastname | timezone         | language | description        | caller_id | outgoing_caller_id | mobile_phone_number | username | password | music_on_hold | preprocess_subroutine | userfield |
            | 1  | James     | Hetfield | America/Montreal | en_US    | Metallica Musician | METAL     | anonymous          | 5551234567          | james    | hetfield | missing       | subroutine            | userfield |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "users" resource
        Then I get a response with a link to the "users" resource
        Then the created user has the following parameters:
            | id | firstname | lastname | timezone         | language | description        | caller_id | outgoing_caller_id | mobile_phone_number | username | password | music_on_hold | preprocess_subroutine | userfield |
            | 1  | James     | Hetfield | America/Montreal | en_US    | Metallica Musician | "METAL"   | anonymous          | 5551234567          | james    | hetfield | missing       | subroutine            | userfield |

    Scenario: Editing a user that doesn't exist
        Given I have no users
        When I update the user with id "1" using the following parameters:
          | firstname |
          | Bob       |
        Then I get a response with status "404"

    Scenario: Editing a user with parameters that don't exist
        Given I only have the following users:
          |     id | firstname | lastname |
          | 995435 | Clémence  | Dupond   |
        When I update the user with id "995435" using the following parameters:
          | unexisting_field |
          | unexisting value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Editing the firstname of a user
        Given I only have the following users:
          |     id | firstname | lastname |
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
        Given I only have the following users:
          |     id | firstname | lastname |
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
        Given I only have the following users:
            | id | firstname | lastname |
            | 42 | Clémence  | Dujas    |
        When I update the user with id "42" using the following parameters:
            | firstname | lastname       | caller_id         |
            | Olivia    | Schtroumpfette | La Schtroumpfette |
        Then I get a response with status "204"
        When I ask for the user with id "42"
        Then I get a user with the following parameters:
            | id | firstname | lastname       | caller_id           |
            | 42 | Olivia    | Schtroumpfette | "La Schtroumpfette" |

    Scenario: Editing only the caller_id of a user
        Given I only have the following users:
            | id | firstname | lastname |
            | 43 | Benoit    | Thierri  |
        When I update the user with id "43" using the following parameters:
            | caller_id        |
            | Grand Schtroumpf |
        Then I get a response with status "204"
        When I ask for the user with id "43"
        Then I get a user with the following parameters:
            | id | firstname | lastname | caller_id          |
            | 43 | Benoit    | Thierri  | "Grand Schtroumpf" |

    Scenario: Editing all available parameters of a user
        Given I only have the following users:
            | id | firstname | lastname | timezone         | language | description        | caller_id | outgoing_caller_id | mobile_phone_number | username | password | music_on_hold | preprocess_subroutine | userfield |
            | 1  | James     | Hetfield | America/Montreal | en_US    | Metallica Musician | METAL     | anonymous          | 5551234567          | james    | hetfield | missing       | subroutine            | userfield |
        When I update the user with id "1" using the following parameters:
            | firstname | lastname | timezone       | language | description | caller_id | outgoing_caller_id | mobile_phone_number | username  | password | music_on_hold | preprocess_subroutine | userfield |
            | Alexander | Powell   | Africa/Abidjan | fr_FR    | updated     | ALEXANDER | default            | 1234567890          | alexander | powell   | default       | other_subroutine      | myvalue   |
        Then I get a response with status "204"
        When I ask for the user with id "1"
        Then I get a user with the following parameters:
            | id | firstname | lastname | timezone       | language | description | caller_id   | outgoing_caller_id | mobile_phone_number | username  | password | music_on_hold | preprocess_subroutine | userfield |
            | 1  | Alexander | Powell   | Africa/Abidjan | fr_FR    | updated     | "ALEXANDER" | default            | 1234567890          | alexander | powell   | default       | other_subroutine      | myvalue   |

    Scenario: Deleting a user that doesn't exist
        Given I have no users
        When I delete the user with id "1"
        Then I get a response with status "404"

    Scenario: Deleting a user
        Given I only have the following users:
          |     id | firstname | lastname |
          | 955135 | Clémence  | Dupond   |
        When I delete the user with id "955135"
        Then I get a response with status "204"
        Then the user with id "955135" no longer exists

    Scenario: Deleting a user still has a link
        Given I only have the following users:
            |     id | firstname | lastname |
            | 956541 | Clémence  | Dupond   |
        Given I only have the following lines:
            |     id | context | protocol | device_slot |
            | 546216 | default | sip      |           1 |
        Given I only have the following extensions:
            |     id | context | exten |
            | 951654 | default |  1000 |
        When I create the following links:
            | user_id | line_id | extension_id | main_line |
            |  956541 |  546216 |       951654 | True      |

        When I delete the user with id "956541"
        Then I get a response with status "400"
        Then I get an error message "Error while deleting User: user still has a link"

    Scenario: List the links associated to a user with no links
        Given I only have the following users:
            |     id | firstname | lastname |
            | 989465 | Francisco | Montoya  |
        When I get the lines associated to user "989465"
        Then I get an empty list

    Scenario: List the links associated to a user
        Given I only have the following users:
            |     id | firstname | lastname |
            | 994775 | Jacen     | Solo     |
            | 112348 | Anakin    | Solo     |
        Given I only have the following lines:
            |     id | context | protocol | device_slot |
            | 135498 | default | sip      |           1 |
            | 133364 | default | sip      |           1 |
        Given I only have the following extensions:
            |     id | context | exten |
            | 995135 | default |  1001 |
            | 132468 | default |  1002 |
        Given the following users, lines, extensions are linked:
            | user_id | line_id | extension_id | main_line |
            |  994775 |  135498 |       995135 | True      |
            |  112348 |  133364 |       132468 | True      |

        When I get the lines associated to user "994775"
        Then I get a response with status "200"
        Then I get the user_links with the following parameters:
            | user_id | line_id | extension_id |
            |  994775 |  135498 |       995135 |
        Then I do not get the user_links with the following parameters:
            | user_id | line_id | extension_id |
            |  112348 |  133364 |       132468 |
