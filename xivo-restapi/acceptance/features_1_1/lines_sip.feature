Feature: SIP Lines

    Scenario: Create an empty SIP line
        When I create an empty SIP line
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: context"

    #FAIL
    Scenario: Create a line with an empty context
        When I create a line with the following properties:
            | context |
            |         |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: context"

    #FAIL
    Scenario: Create a line with a context that doesn't exist
        When I create a line with the following properties:
            | context           |
            | superdupercontext |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: context"

    Scenario: Create a line with invalid parameters
        When I create a line with the following properties:
            | context | invalidparameter |
            | default | invalidvalue     |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: invalidparameter"

    Scenario: Create a line with a context
        When I create a line with the following properties:
            | context |
            | default |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a response with a link to the "lines_sip" resource
        Then I get a header with a location for the "lines_sip" resource
        #Then I see the line in the webi

    Scenario: Create a line with an internal context other than default
        Given I have an internal context named "mycontext"
        When I create a line with the following properties:
            | context     |
            | mycontext   |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a response with a link to the "lines_sip" resource
        Then I get a header with a location for the "lines_sip" resource
        #Then I see the line in the webi

    Scenario: Create 2 lines in same context
        When I create a line with the following properties:
            | context |
            | default |
        Then I get a response with status "201"
        When I create a line with the following properties:
            | context |
            | default |
        Then I get a response with status "201"
        #Then i see 2 lines in the webi
