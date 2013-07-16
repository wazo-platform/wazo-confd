Feature: Users

    Scenario: User list with no users
        Given there are no users
        When I ask for the list of users
        Then I get an empty list

    Scenario: User list with one user
        Given there are only the following users:
          | firstname | lastname |
          | Clémence  | Dupond   |
        When I ask for the list of users
        Then I get a list with the following users:
          | firstname | lastname | userfield |
          | Clémence  | Dupond   |           |

    Scenario: User list with two users
        Given there are only the following users:
          | firstname | lastname |
          | Clémence  | Dupond   |
          | Louis     | Martin   |
        When I ask for the list of users
        Then I get a list with the following users:
          | firstname | lastname | userfield |
          | Clémence  | Dupond   |           |
          | Louis     | Martin   |           |

    Scenario: User list ordered by lastname, then firstname
        Given there are only the following users:
          | firstname | lastname |
          | Clémence  | Dupond   |
          | Louis     | Martin   |
          | Albert    | Dupond   |
          | Frédéric  | Martin   |
        When I ask for the list of users
        Then I get a list with the following users:
          | firstname | lastname | userfield |
          | Albert    | Dupond   |           |
          | Clémence  | Dupond   |           |
          | Frédéric  | Martin   |           |
          | Louis     | Martin   |           |

    Scenario: User search with no users
        Given there are no users
        When I search for the user "Bob"
        Then I get an empty list

    Scenario: User search with an empty filter
        Given there are only the following users:
          | firstname | lastname |
          | George    | Lucas    |
        When I search for the user ""
        Then I get a list with the following users:
         | firstname | lastname |
         | George    | Lucas    |

    Scenario: User search with a filter that returns nothing
        Given there are only the following users:
          | firstname | lastname |
          | Andreï    | Bélier   |
        When I search for the user "bob"
        Then I get an empty list
        When I search for the user "rei"
        Then I get an empty list

    Scenario: User search using the firstname
        Given there are only the following users:
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
        Given there are only the following users:
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
        Given there are only the following users:
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
        Given there are only the following users:
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
        Given there are no users
        When I ask for the user with id "1"
        Then I get a response with status "404"

    Scenario: Getting a user that exists
        Given there are only the following users:
          | id | firstname | lastname |
          | 1  | Irène     | Dupont   |
        When I ask for the user with id "1"
        Then I get a response with status "200"
        Then I get a user with the following properties:
          | id | firstname | lastname | userfield |
          | 1  | Irène     | Dupont   |           |

    Scenario: Getting a user with his voicemail
        Given there are only the following users:
          | id | firstname | lastname | line number | voicemail number | language |
          | 1  | Irène     | Dupont   | 1000        | 1000             | fr_FR    |
        When I ask for user "Irène Dupont", including his voicemail
        Then I get a response with status "200"
        Then I get a user with the following properties:
          | firstname | lastname | userfield |
          | Irène     | Dupont   |           |
        Then I get a user with a voicemail

    Scenario: Creating an empty user
        Given there are no users
        When I create an empty user
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: firstname"

    Scenario: Creating a user with paramters that don't exist
        Given there are no users
        When I create users with the following parameters:
          | unexisting_field |
          | unexisting_value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Creating a user with a firstname and parameters that don't exist
        Given there are no users
        When I create users with the following parameters:
          | firstname | unexisting_field |
          | Joe       | unexisting_value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Creating a user with a firstname
        Given there are no users
        When I create users with the following parameters:
          | firstname |
          | Irène     |
        Then I get a response with status "201"
        Then I get a response with a user id
        Then I get a response header with a location for the new user
        Then the created user has the following parameters:
         | firstname | lastname | userfield |
         | Irène     |          |           |

    Scenario: Creating two users with the same firstname
        Given there are no users
        When I create users with the following parameters:
          | firstname |
          | Lord      |
          | Lord      |
        When I ask for the list of users
        Then I get a list with the following users:
          | firstname | lastname | userfield |
          | Lord      |          |           |
          | Lord      |          |           |

    Scenario: Creating a user with a firstname, lastname, description and userfield
        Given there are no users
        When I create users with the following parameters:
          | firstname | lastname | description                 | userfield  |
          | Irène     | Dupont   | accented description: éà@'; | customdata |
        Then I get a response with status "201"
        Then I get a response with a user id
        Then I get a response header with a location for the new user
        Then the created user has the following parameters:
          | firstname | lastname | description                 | userfield  |
          | Irène     | Dupont   | accented description: éà@'; | customdata |

    Scenario: Editing a user that doesn't exist
        Given there are no users
        When I update the user with id "1" using the following parameters:
          | firstname |
          | Bob       |
        Then I get a response with status "404"

    Scenario: Editing a user with parameters that don't exist
        Given there are only the following users:
          | id | firstname | lastname |
          | 1  | Clémence  | Dupond   |
        When I update the user with id "1" using the following parameters:
          | unexisting_field |
          | unexisting value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Editing the firstname of a user
        Given there are only the following users:
          | id | firstname | lastname |
          | 1  | Clémence  | Dupond   |
        When I update the user with id "1" using the following parameters:
          | firstname |
          | Brézé     |
        Then I get a response with status "204"
        When I ask for the user with id "1"
        Then I get a user with the following properties:
          | id | firstname | lastname | userfield |
          | 1  | Brézé     | Dupond   |           |

    Scenario: Editing the lastname of a user
        Given there are only the following users:
          | id | firstname | lastname |
          | 1  | Clémence  | Dupond   |
        When I update the user with id "1" using the following parameters:
          | lastname      |
          | Argentine     |
        Then I get a response with status "204"
        When I ask for the user with id "1"
        Then I get a user with the following properties:
          | id | firstname | lastname  | userfield |
          | 1  | Clémence  | Argentine |           |

    Scenario: Editing the firstname, lastname and userfield of a user
        Given there are only the following users:
          | id | firstname | lastname |
          | 1  | Clémence  | Dupond   |
        When I update the user with id "1" using the following parameters:
          | firstname | lastname  | userfield  |
          | Claude    | Argentine | customdata |
        Then I get a response with status "204"
        When I ask for the user with id "1"
        Then I get a user with the following properties:
          | id | firstname | lastname  | userfield  |
          | 1  | Claude    | Argentine | customdata |

    Scenario: Deleting a user that doesn't exist
        Given there are no users
        When I delete the user with id "1"
        Then I get a response with status "404"

    Scenario: Deleting a user
        Given there are only the following users:
          | id | firstname | lastname |
          | 1  | Clémence  | Dupond   |
        When I delete the user with id "1"
        Then I get a response with status "204"
        Then the user with id "1" no longer exists
