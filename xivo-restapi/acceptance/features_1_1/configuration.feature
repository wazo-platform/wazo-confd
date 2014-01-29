Feature: REST API Configuration

    Scenario: Get live reload status
        Given a live reload configuration is enable
        When I ask for the live reload state
        Then I get a response with status "200"
        Then I get a response with live reload enabled

    Scenario: Disable live reload and use the webi
        Given a live reload configuration is enable
        When I disable the live reload
        Then I get a response with status "204"
        When i edit extenfeatures page
        Then i see no live reload request in daemon log file

    Scenario: Disable live reload and use Rest API
        Given a live reload configuration is enable
        When I disable the live reload
        Then I get a response with status "204"
        When I wait 10 seconds
        When I create users with the following parameters:
            | firstname | lastname |
            | Joe       |      Doe |
        Then i see no live reload request in daemon log file

    Scenario: Enable live reload
        Given a live reload configuration is disable
        When I enable the live reload
        Then I get a response with status "204"
        Then the CTI is notified for a configuration change
        When i edit extenfeatures page
        Then i see live reload request in daemon log file
        When I create users with the following parameters:
            | firstname | lastname |
            | Joe       |      Doe |
        Then i see live reload request in daemon log file

