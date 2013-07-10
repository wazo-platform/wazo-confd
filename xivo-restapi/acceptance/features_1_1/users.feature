Feature: Users

    Scenario: User list with no users
        Given there are no users
        When I ask for the list of users
        Then I get an empty list

    Scenario: User list with one user
        Given there are the following users:
          | firstname | lastname |
          | Clémence  | Dupond   |
        When I ask for the list of users
        Then I get a list with the following users:
          | firstname | lastname | userfield |
          | Clémence  | Dupond   |           |

    Scenario: User list with two users
        Given there are the following users:
          | firstname | lastname |
          | Clémence  | Dupond   |
          | Louis     | Martin   |
        When I ask for the list of users
        Then I get a list with the following users:
          | firstname | lastname | userfield |
          | Clémence  | Dupond   |           |
          | Louis     | Martin   |           |

    Scenario: User list ordered by lastname, then firstname
        Given there are the following users:
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

    Scenario: Getting a user that doesn't exist
        Given there are no users
        When I ask for the user with id "1"
        Then I get a response with status "404"

    Scenario: Getting a user that exists
        Given there are the following users:
          | id | firstname | lastname |
          | 1  | Irène     | Dupont   |
        When I ask for the user with id "1"
        Then I get a user with the following properties:
          | id | firstname | lastname | userfield |
          | 1  | Irène     | Dupont   |           |

    Scenario: Creating an empty user
        Given there are no users
        When I create an empty user
        Then I get a response with status "400"
        Then I get an error message "Missing paramters: firstname"

    Scenario: Creating a user with paramters that don't exist
        Given there are no users
        When I create users with the following parameters:
          | unexisting_field |
          | unexisting_value |
        Then I get a response with status "400"
        Then I get an error message "Incorrect parameters: unexisting_field"

    Scenario: Creating a user with a firstname and parameters that don't exist
        Given there are no users
        When I create users with the following parameters:
          | firstname | unexisting_field |
          | Joe       | unexisting_value |
        Then I get a response with status "400"
        Then I get an error message "Incorrect parameters: unexisting_field"

    Scenario: Creating a user with a firstname
        Given there are no users
        When I create users with the following parameters:
          | firstname |
          | Irène     |
        Then I get a response with status "201"
        Then I get a response with a user id

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

    Scenario: Creating a user with a firstname, lastname and description
        Given there are no users
        When I create users with the following parameters:
          | firstname | lastname | description                 |
          | Irène     | Dupont   | accented description: éà@'; |
        Then I get a response with status "201"
        Then I get a response with a user id

    Scenario: Editing a user that doesn't exist
        Given there are no users
        When I update the user with id "1" using the following parameters:
          | firstname |
          | Bob       |
        Then I get a response with status "404"

    Scenario: Editing a user with parameters that don't exist
        Given there are the following users:
          | id | firstname | lastname |
          | 1  | Clémence  | Dupond   |
        When I update the user with id "1" using the following parameters:
          | unexisting_field |
          | unexisting value |
        Then I get a response with status "400"
        Then I get an error message "Incorrect parameters: unexisting_field"

    Scenario: Editing the firstname of a user
        Given there are the following users:
          | id | firstname | lastname |
          | 1  | Clémence  | Dupond   |
        When I update the user with id "1" using the following parameters:
          | firstname |
          | Brézé     |
        Then I get a response with status "204"
        When I ask for user with id "1"
        Then I get a user with the following properties:
          | id | firstname | lastname | userfield |
          | 1  | Brézé     | Dupont   |           |

    Scenario: Editing the lastname of a user
        Given there are the following users:
          | id | firstname | lastname |
          | 1  | Clémence  | Dupond   |
        When I update the user with id "1" using the following parameters:
          | lastname      |
          | Argentine     |
        Then I get a response with status "204"
        When I ask for user with id "1"
        Then I get a user with the following properties:
          | id | firstname | lastname  | userfield |
          | 1  | Clémence  | Argentine |           |

    Scenario: Deleting a user that doesn't exist
        Given there are no users
        When I delete the user with id "1"
        Then I get a response with status "404"

    Scenario: Deleting a user
        Given there are the following users:
          | id | firstname | lastname |
          | 1  | Clémence  | Dupond   |
        When I delete the user with id "1"
        Then I get a response with status "204"
        Then the user with id "1" no longer exists
