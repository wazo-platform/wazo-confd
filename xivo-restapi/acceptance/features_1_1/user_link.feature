Feature: REST API Link user with a line and extension

    Scenario: Create an empty link
        When I create an empty link
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: user_id,line_id,extension_id"

    Scenario: Create a link with empty parameters
        When I create a link with the following invalid parameters:
            | user_id | extension_id | line_id |
            |         |              |         |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: user_id must be integer,line_id must be integer,extension_id must be integer"

    Scenario: Create a link with invalid values
        When I create a link with the following invalid parameters:
            | user_id | extension_id | line_id |
            | asdf    | 1            | 2       |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: user_id must be integer,line_id must be integer,extension_id must be integer"

    Scenario: Create a link with invalid parameters
        When I create the following links:
            | user_id | extension_id | line_id | invalid |
            | 3       | 1            | 2       | invalid |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: invalid"

    Scenario: Create a link with a missing line id
        When I create the following links:
            | user_id | extension_id |
            | 1       | 2            |
        Then I get a response with status "400"
        Then I get an error message "Missing parameters: line_id"

    Scenario: Create link with an extension that doesn't exist
        Given I have no extension with id "534478"
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 452483 | Greg      | Sanderson |
        Given I have the following lines:
            |     id | context | protocol | device_slot |
            | 954318 | default | sip      |           1 |
        When I create the following links:
            | user_id | line_id | extension_id |
            |  452483 |  954318 |       534478 |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: extension_id 534478 does not exist"

    Scenario: Create link with a line that doesn't exist
        Given I have no line with id "534835"
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 553178 | Greg      | Sanderson |
        Given I have the following extensions:
            |     id | context | exten |
            | 961348 | default |  1000 |
        When I create the following links:
            | user_id | line_id | extension_id |
            |  553178 |  534835 |       961348 |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: line_id 534835 does not exist"

    Scenario: Create link with a user that doesn't exist
        Given I have no users
        Given I have the following lines:
            |     id | context | protocol | device_slot |
            | 839943 | default | sip      |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 153489 | default |  1000 |
        When I create the following links:
            | user_id | line_id | extension_id |
            |  889643 |  839943 |       153489 |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: user_id 889643 does not exist"

    Scenario: Create link with an extension outside of context user range
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 134684 | Greg      | Sanderson |
        Given I have the following lines:
            |     id | context | protocol | device_slot |
            | 963148 | default | sip      |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 132469 | default |  3000 |
        When I create the following links:
            | user_id | line_id | extension_id |
            |  134684 |  963148 |       132469 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: Exten 3000 not inside user range of context default"

    Scenario: Create a link
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 542357 | Greg      | Sanderson |
        Given I have the following lines:
            |     id | context | protocol | device_slot |
            | 132494 | default | sip      |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 961347 | default |  1000 |
        When I create the following links:
            | user_id | line_id | extension_id |
            |  542357 |  132494 |       961347 |
        Then I get a response with status "201"

        Then I get a response with a link to the "user_links" resource
        Then I get a response with a link to the "extensions" resource with id "961347"
        Then I get a response with a link to the "lines" resource with id "132494"
        Then I get a response with a link to the "users" resource with id "542357"
        Then I get a header with a location for the "user_links" resource

    Scenario: Create a link in another context
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 134697 | Greg      | Sanderson |
        Given I have the following lines:
            |     id | context     | protocol | device_slot |
            | 632147 | statscenter | sip      |           1 |
        Given I have the following extensions:
            |     id | context     | exten |
            | 136679 | statscenter |  1000 |
        When I create the following links:
            | user_id | line_id | extension_id |
            |  134697 |  632147 |       136679 |
        Then I get a response with status "201"
        Then I get a response with a link to the "user_links" resource
        Then I get a response with a link to the "extensions" resource with id "136679"
        Then I get a response with a link to the "lines" resource with id "632147"
        Then I get a response with a link to the "users" resource with id "134697"
        Then I get a header with a location for the "user_links" resource

    Scenario: Associate 3 users to the same line/extension
        Given I have the following lines:
            |     id | context | protocol | device_slot |
            | 563479 | default | sip      |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 136974 | default |  1000 |
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 659434 | Salle     | Doctorant |
            | 698431 | Greg      | Sanderson |
            | 136698 | Roberto   | Da Silva  |
        When I create the following links:
            | user_id | line_id | extension_id | main_user |
            |  659434 |  563479 |       136974 | True      |
            |  698431 |  563479 |       136974 | False     |
            |  136698 |  563479 |       136974 | False     |
        Then I get a response with status "201"

        Then I see a user with infos:
            | fullname        | protocol | context | number |
            | Salle Doctorant | sip      | default | 1000   |
        When I edit the user "Salle" "Doctorant" without changing anything
        Then I see a user with infos:
            | fullname        | protocol | context | number |
            | Salle Doctorant | sip      | default | 1000   |

        Then I see a user with infos:
            | fullname       | protocol | context | number |
            | Greg Sanderson | sip      | default | 1000   |
        When I edit the user "Greg" "Sanderson" without changing anything
        Then I see a user with infos:
            | fullname       | protocol | context | number |
            | Greg Sanderson | sip      | default | 1000   |

        Then I see a user with infos:
            | fullname         | protocol | context | number |
            | Roberto Da Silva | sip      | default | 1000   |
        When I edit the user "Roberto" "Da Silva" without changing anything
        Then I see a user with infos:
            | fullname         | protocol | context | number |
            | Roberto Da Silva | sip      | default | 1000   |

    Scenario: Create a link with a provision device
        Given I only have the following users:
            | id | firstname | lastname  |
            | 995437 | Greg      | Sanderson |
        Given I have the following lines:
            | id | context | protocol | username | secret | device_slot |
            | 963249 | default | sip      | toto     | tata   | 1           |
        Given I have the following extensions:
            | id  | context | exten |
            | 663461 | default | 1000  |
        Given I only have the following devices:
            | id              |       ip |               mac |
            | a321cc6f334b68d | 10.0.0.1 | 00:00:00:00:00:00 |
        When I create the following links:
            | user_id | line_id | extension_id |
            |  995437 |  963249 |       663461 |
        Then I get a response with status "201"

        Then I get a response with a link to the "user_links" resource
        Then I get a response with a link to the "extensions" resource with id "663461"
        Then I get a response with a link to the "lines" resource with id "963249"
        Then I get a response with a link to the "users" resource with id "995437"
        Then I get a header with a location for the "user_links" resource

        When I provision my device with my line_id "963249" and ip "10.0.0.1"
        Then the device "a321cc6f334b68d" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | toto     | toto          | tata     |

    Scenario: Link 2 users to a line
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 989432 | Greg      | Sanderson |
            | 136549 | Cédric    | Abunar    |
        Given I have the following lines:
            |     id | context | protocol | device_slot |
            | 322416 | default | sip      |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 562168 | default |  1000 |

        When I create the following links:
            | user_id | line_id | extension_id |
            |  989432 |  322416 |       562168 |
        Then I get a response with status "201"
        Then I get a response with a link to the "user_links" resource
        Then I get a response with the following link resources:
            | resource   |     id |
            | users      | 989432 |
            | lines      | 322416 |
            | extensions | 562168 |

        When I create the following links:
            | user_id | line_id | extension_id |
            |  136549 |  322416 |       562168 |
        Then I get a response with status "201"
        Then I get a response with a link to the "user_links" resource
        Then I get a response with the following link resources:
            | resource   |     id |
            | users      | 136549 |
            | lines      | 322416 |
            | extensions | 562168 |

    Scenario: Link a user already associated to a line
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 168874 | Greg      | Sanderson |
        Given I have the following lines:
            |     id | context | protocol | device_slot |
            | 168746 | default | sip      |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 996247 | default |  1000 |

        When I create the following links:
            | user_id | line_id | extension_id |
            |  168874 |  168746 |       996247 |
        Then I get a response with status "201"
        When I create the following links:
            | user_id | line_id | extension_id |
            |  168874 |  168746 |       996247 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: user is already associated to this line"

    Scenario: Link an extension already associated to another line
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 951324 | Greg      | Sanderson |
            | 969517 | Hello     | Dolly     |
        Given I have the following lines:
            |     id | context | protocol | device_slot |
            | 654324 | default | sip      |           1 |
            | 216587 | default | sip      |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 413244 | default |  1000 |
        Given the following users, lines, extensions are linked:
            | user_id | line_id | extension_id |
            |  951324 |  654324 |       413244 |
        When I create the following links:
            | user_id | line_id | extension_id |
            |  969517 |  216587 |       413244 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: Extension 1000@default already linked to a line"

    Scenario: Provision a device for 2 users
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 696547 | Greg      | Sanderson |
            | 195474 | Cédric    | Abunar    |
        Given I have the following lines:
            |     id | context | protocol | username | secret | device_slot |
            | 443576 | default | sip      | abc123   | def456 |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 665445 | default |  1000 |
        Given I only have the following devices:
            | id              |       ip |               mac |
            | 5256ac652e65c4f | 10.0.0.1 | 00:00:00:00:00:00 |
        When I create the following links:
            | user_id | line_id | extension_id |
            |  696547 |  443576 |       665445 |
            |  195474 |  443576 |       665445 |
        When I provision my device with my line_id "443576" and ip "10.0.0.1"
        Then the device "5256ac652e65c4f" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | abc123   | abc123        | def456   |

    Scenario: Link a second user after provisioning a device
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 523215 | Greg      | Sanderson |
            | 135579 | Cédric    | Abunar    |
        Given I have the following lines:
            |     id | context | protocol | username | secret | device_slot |
            | 898479 | default | sip      | abc123   | def456 |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 954496 | default |  1000 |
        Given I only have the following devices:
            | id                 |       ip |               mac |
            | 56995af6622c6e26cc | 10.0.0.1 | 00:00:00:00:00:00 |

        When I create the following links:
            | user_id | line_id | extension_id |
            |  523215 |  898479 |          954496    |
        Then I get a response with status "201"
        When I provision my device with my line_id "898479" and ip "10.0.0.1"
        Then the device "56995af6622c6e26cc" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | abc123   | abc123        | def456   |

        When I create the following links:
            | user_id | line_id | extension_id |
            |  135579 |  898479 |       954496 |
        Then I get a response with status "201"
        Then the device "56995af6622c6e26cc" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | abc123   | abc123        | def456   |

    Scenario: Create a link with a provision device and update user callerid
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 954986 | Greg      | Sanderson |
        Given I have the following lines:
            |     id | context | protocol | username | secret | device_slot |
            | 996247 | default | sip      | toto     | tata   |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 136879 | default |  1000 |
        Given I only have the following devices:
            |     id |       ip |               mac |
            | 331684 | 10.0.0.1 | 00:00:00:00:00:00 |
        When I create the following links:
            | user_id | line_id | extension_id |
            |  954986 |  996247 |       136879 |
        Then I get a response with status "201"
        Then I get a response with a link to the "user_links" resource
        Then I get a response with a link to the "extensions" resource with id "136879"
        Then I get a response with a link to the "lines" resource with id "996247"
        Then I get a response with a link to the "users" resource with id "954986"
        Then I get a header with a location for the "user_links" resource

        When I provision my device with my line_id "996247" and ip "10.0.0.1"
        Then the device "331684" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | toto     | toto          | tata     |
        When I update the user with id "954986" using the following parameters:
            | firstname | lastname  |
            | Gregory   | Sanderson |
        Then the device "331684" has been provisioned with a configuration:
            | display_name      | number | username | auth_username | password |
            | Gregory Sanderson | 1000   | toto     | toto          | tata     |

    Scenario: Delete a user link that doesn't exist
        Given I have no link with the following parameters:
            | id |
            | 2  |
        When I delete the following links:
            | id |
            | 2  |
        Then I get a response with status "404"
        Then I get an error message "UserLineExtension with id=2 does not exist"

    Scenario: Delete secondary user
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 662149 | Greg      | Sanderson |
            | 136624 | Cédric    | Abunar    |
        Given I have the following lines:
            |     id | context | protocol | username | secret | device_slot |
            | 699734 | default | sip      | toto     | tata   |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 133349 | default |  1000 |

        When I create the following links:
            |     id | user_id | line_id | extension_id |
            | 992463 |  662149 |  699734 |       133349 |
            | 443248 |  136624 |  699734 |       133349 |
        Then I get a response with status "201"

        When I delete the following links:
            |     id |
            | 443248 |
        Then I get a response with status "204"

    Scenario: Delete a secondary user after provisioning a device
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 992435 | Greg      | Sanderson |
            | 332169 | Cédric    | Abunar    |
        Given I have the following lines:
            |     id | context | protocol | username | secret | device_slot |
            | 952416 | default | sip      | toto     | tata   |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 132499 | default |  1000 |
        Given I only have the following devices:
            | id            |       ip |               mac |
            | 665aeb6c5d66f | 10.0.0.1 | 00:00:00:00:00:00 |

        When I create the following links:
            |     id | user_id | line_id | extension_id |
            | 995434 |  992435 |  952416 |       132499 |
            | 449521 |  332169 |  952416 |       132499 |
        Then I get a response with status "201"

        When I provision my device with my line_id "952416" and ip "10.0.0.1"
        Then the device "665aeb6c5d66f" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | toto     | toto          | tata     |

        When I delete the following links:
            |     id |
            | 449521 |
        Then I get a response with status "204"
        Then the device "665aeb6c5d66f" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | toto     | toto          | tata     |

    Scenario: Delete main user
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 585866 | Greg      | Sanderson |
            | 158479 | Cédric    | Abunar    |
        Given I have the following lines:
            |     id | context | protocol | username | secret | device_slot |
            | 995434 | default | sip      | toto     | tata   |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 995435 | default |  1000 |

        When I create the following links:
            |     id | user_id | line_id | extension_id |
            | 995476 |  585866 |  995434 |       995435 |
            | 113684 |  158479 |  995434 |       995435 |
        Then I get a response with status "201"

        When I delete the following links:
            |     id |
            | 995476 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: There are secondary users associated to this link"

    Scenario: Delete main user after provisioning a device still has a secondary user
        Given I only have the following users:
            |     id | firstname | lastname  |
            | 895432 | Greg      | Sanderson |
            | 995462 | Cédric    | Abunar    |
        Given I have the following lines:
            |     id | context | protocol | username | secret | device_slot |
            | 995474 | default | sip      | toto     | tata   |           1 |
        Given I have the following extensions:
            |     id | context | exten |
            | 443221 | default |  1000 |
        Given I only have the following devices:
            | id              |       ip |               mac |
            | 5566ac632e6df54 | 10.0.0.1 | 00:00:00:00:00:00 |

        When I create the following links:
            |     id | user_id | line_id | extension_id |
            | 651355 |  895432 |  995474 |       443221 |
            | 954324 |  995462 |  995474 |       443221 |

        When I provision my device with my line_id "995474" and ip "10.0.0.1"
        Then the device "5566ac632e6df54" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | toto     | toto          | tata     |

        When I delete the following links:
            |     id |
            | 651355 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: There are secondary users associated to this link"
