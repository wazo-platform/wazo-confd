Feature: Users

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
          | firstname | lastname | userfield |
          | Clémence  | Dupond   |           |

    Scenario: User list with two users
        Given I only have the following users:
          | firstname | lastname |
          | Clémence  | Dupond   |
          | Louis     | Martin   |
        When I ask for the list of users
        Then I get a list with the following users:
          | firstname | lastname | userfield |
          | Clémence  | Dupond   |           |
          | Louis     | Martin   |           |

    Scenario: User list ordered by lastname, then firstname
        Given I only have the following users:
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
        Given I have no users
        When I search for the user "Bob"
        Then I get an empty list

    Scenario: User search with an empty filter
        Given I only have the following users:
          | firstname | lastname |
          | George    | Lucas    |
        When I search for the user ""
        Then I get a list with the following users:
         | firstname | lastname |
         | George    | Lucas    |

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
         | firstname | lastname | userfield |
         | Irène     |          |           |

    Scenario: Creating two users with the same firstname
        Given I have no users
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
        Given I have no users
        When I create users with the following parameters:
          | firstname | lastname | description                 | userfield  |
          | Irène     | Dupont   | accented description: éà@'; | customdata |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "users" resource
        Then I get a response with a link to the "users" resource
        Then the created user has the following parameters:
          | firstname | lastname | description                 | userfield  |
          | Irène     | Dupont   | accented description: éà@'; | customdata |

    Scenario: Editing a user that doesn't exist
        Given I have no users
        When I update the user with id "1" using the following parameters:
          | firstname |
          | Bob       |
        Then I get a response with status "404"

    Scenario: Editing a user with parameters that don't exist
        Given I only have the following users:
          | id | firstname | lastname |
          | 1  | Clémence  | Dupond   |
        When I update the user with id "1" using the following parameters:
          | unexisting_field |
          | unexisting value |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: unexisting_field"

    Scenario: Editing the firstname of a user
        Given I only have the following users:
          | id | firstname | lastname |
          | 1  | Clémence  | Dupond   |
        When I update the user with id "1" using the following parameters:
          | firstname |
          | Brézé     |
        Then I get a response with status "204"
        When I ask for the user with id "1"
        Then I get a user with the following parameters:
          | id | firstname | lastname | userfield |
          | 1  | Brézé     | Dupond   |           |

    Scenario: Editing the lastname of a user
        Given I only have the following users:
          | id | firstname | lastname |
          | 1  | Clémence  | Dupond   |
        When I update the user with id "1" using the following parameters:
          | lastname      |
          | Argentine     |
        Then I get a response with status "204"
        When I ask for the user with id "1"
        Then I get a user with the following parameters:
          | id | firstname | lastname  | userfield |
          | 1  | Clémence  | Argentine |           |

    Scenario: Editing the firstname, lastname and userfield of a user
        Given I only have the following users:
          | id | firstname | lastname |
          | 1  | Clémence  | Dupond   |
        When I update the user with id "1" using the following parameters:
          | firstname | lastname  | userfield  |
          | Claude    | Argentine | customdata |
        Then I get a response with status "204"
        When I ask for the user with id "1"
        Then I get a user with the following parameters:
          | id | firstname | lastname  | userfield  |
          | 1  | Claude    | Argentine | customdata |

    Scenario: Deleting a user that doesn't exist
        Given I have no users
        When I delete the user with id "1"
        Then I get a response with status "404"

    Scenario: Deleting a user
        Given I only have the following users:
          | id | firstname | lastname |
          | 1  | Clémence  | Dupond   |
        When I delete the user with id "1"
        Then I get a response with status "204"
        Then the user with id "1" no longer exists

    Scenario: List the links associated to a user with no links
        Given I only have the following users:
            | id | firstname | lastname |
            | 1  | Francisco | Montoya  |
        When I get the lines associated to a user "1"
        Then I get a response with status "404"

    Scenario: List the links associated to a user
        Given I only have the following users:
            | id | firstname | lastname |
            | 1  | Francisco | Montoya  |
        Given I only have the following lines_sip:
            | id | context | protocol |
            | 10 | default | sip      |
            | 20 | default | sip      |
        Given I only have the following extensions:
            | id  | context | exten | type | typeval |
            | 100 | default | 1000  | user | 1       |
        When I create a link with the following parameters:
            | user_id | line_id | extension_id | main_line |
            | 1       | 10      | 100          | True      |
            | 1       | 20      | 100          | False     |
        Then I get a response with status "201"
        Then I get a response with a link to the "user_links" resource
        Then I get a header with a location for the "user_links" resource
        
        When I get the lines associated to a user "1"
        Then I get a response with status "200"
        Then I get the user_links with the following parameters:
            | user_id | line_id | extension_id | main_line |
            | 1       | 10      | 100          | True      |
            | 1       | 20      | 100          | False     |
