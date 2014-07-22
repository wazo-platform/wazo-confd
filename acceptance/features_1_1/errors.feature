Feature: Error Messages

    Scenario Outline: Create a resource with missing parameters
        When I POST the following content at url "<url>":
            """
            <document>
            """
        Then I get a response 400 matching "Missing parameters: <parameters>"

    Examples:
        | url            | document | parameters |
        | /users/1/lines | {}       | line_id    |

    Scenario Outline: Create a resource with invalid parameter type
        When I POST the following content at url "<url>":
            """
            <document>
            """
        Then I get a response 400 matching "Error while validating field '<field>': '\w*' is not <message>"

    Examples:
        | url            | document                                                                          | field        | message    |
        | /lines_sip     | {"device_slot": ""}                                                               | device_slot  | an integer |
        | /lines_sip     | {"device_slot": "toto"}                                                           | device_slot  | an integer |
        | /users/1/lines | {"line_id": "toto"}                                                               | line_id      | an integer |
        | /voicemails    | {"max_messages": "zero"}                                                          | max_messages | an integer |

    Scenario Outline: Create a resource with invalid parameters
        When I POST the following content at url "<url>":
            """
            <document>
            """
        Then I get a response 400 matching "Invalid parameters: <message>"

    Examples:
        | url            | document                                                                          | message                            |
        | /lines_sip     | {"device_slot": 0, "context": "default"}                                          | device_slot must be greater than 0 |
        | /lines_sip     | {"device_slot": -1, "context": "default"}                                         | device_slot must be greater than 0 |
        | /lines_sip     | {"device_slot": 1, "context": ""}                                                 | context cannot be empty            |
        | /lines_sip     | {"invalid": "invalid"}                                                            | invalid                            |
        | /users/1/lines | {"invalid": "invalid"}                                                            | invalid                            |
        | /voicemails    | {"name": "voicemail", "number": "1000", "context": "default", "max_messages": -4} | max_messages                       |
