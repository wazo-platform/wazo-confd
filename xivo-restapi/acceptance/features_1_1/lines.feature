Feature: Lines

    Scenario: Line list with no lines
        Given I have no lines
        When I ask for the list of lines
        Then I get an empty list
