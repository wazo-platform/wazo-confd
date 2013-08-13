Feature: SIP Lines

    Scenario: Create an empty SIP line
        When I create an empty SIP line
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: context"

    Scenario: Create a line with an empty context
        When I create a line with the following parameters:
            | context |
            |         |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: context cannot be empty"

    Scenario: Create a line with a context that doesn't exist
        When I create a line with the following parameters:
            | context           |
            | superdupercontext |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: context superdupercontext does not exist"

    Scenario: Create a line with invalid parameters
        When I create a line with the following parameters:
            | context | invalidparameter |
            | default | invalidvalue     |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: invalidparameter"

    Scenario: Create a line with a context
        When I create a line with the following parameters:
            | context |
            | default |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a response with a link to the "lines_sip" resource
        Then I get a header with a location for the "lines_sip" resource

    Scenario: Create a line with an internal context other than default
        Given I have an internal context named "mycontext"
        When I create a line with the following parameters:
            | context     |
            | mycontext   |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a response with a link to the "lines_sip" resource
        Then I get a header with a location for the "lines_sip" resource

    Scenario: Create 2 lines in same context
        When I create a line with the following parameters:
            | context |
            | default |
        Then I get a response with status "201"
        When I create a line with the following parameters:
            | context |
            | default |
        Then I get a response with status "201"
