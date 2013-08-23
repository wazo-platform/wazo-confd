Feature: Link user with a line and extension

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
        Given I have no extensions
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        Given I only have the following lines:
            | id | context | protocol | device_slot |
            | 10 | default | sip      | 1           |
        When I create the following links:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: extension_id 100 does not exist"

    Scenario: Create link with a line that doesn't exist
        Given I have no lines
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        When I create the following links:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: line_id 10 does not exist"

    Scenario: Create link with a user that doesn't exist
        Given I have no users
        Given I only have the following lines:
            | id | context | protocol | device_slot |
            | 10 | default | sip      | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        When I create the following links:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: user_id 1 does not exist"

    Scenario: Create a link
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        Given I only have the following lines:
            | id | context | protocol | device_slot |
            | 10 | default | sip      | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        When I create the following links:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "201"

        Then I get a response with a link to the "user_links" resource
        Then I get a response with a link to the "extensions" resource with id "100"
        Then I get a response with a link to the "lines" resource with id "10"
        Then I get a response with a link to the "users" resource with id "1"
        Then I get a header with a location for the "user_links" resource

    Scenario: Create a link in another context
        Given I only have the following users:
            | id  | firstname | lastname  |
            | 1   | Greg      | Sanderson |
        Given I only have the following lines:
            | id | context     | protocol | device_slot |
            | 10 | statscenter | sip      | 1           |
        Given I only have the following extensions:
            | id  | context     | exten |
            | 100 | statscenter | 1000  |
        When I create the following links:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "201"
        Then I get a response with a link to the "user_links" resource
        Then I get a response with a link to the "extensions" resource with id "100"
        Then I get a response with a link to the "lines" resource with id "10"
        Then I get a response with a link to the "users" resource with id "1"
        Then I get a header with a location for the "user_links" resource

    Scenario: Associate 3 users to the same line/extension
        Given I only have the following lines:
            | id | context | protocol | device_slot |
            | 10 | default | sip      | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Salle     | Doctorant |
            | 2  | Greg      | Sanderson |
            | 3  | Roberto   | Da Silva  |
        When I create the following links:
            | user_id | line_id | extension_id | main_user |
            | 1       | 10      | 100          | True      |
            | 2       | 10      | 100          | False     |
            | 3       | 10      | 100          | False     |
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
            | 1  | Greg      | Sanderson |
        Given I only have the following lines:
            | id | context | protocol | username | secret | device_slot |
            | 10 | default | sip      | toto     | tata   | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        Given I only have the following devices:
            | id | ip       | mac               |
            | 20 | 10.0.0.1 | 00:00:00:00:00:00 |
        When I create the following links:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "201"

        Then I get a response with a link to the "user_links" resource
        Then I get a response with a link to the "extensions" resource with id "100"
        Then I get a response with a link to the "lines" resource with id "10"
        Then I get a response with a link to the "users" resource with id "1"
        Then I get a header with a location for the "user_links" resource

        When I provision my device with my line_id "10" and ip "10.0.0.1"
        Then the device "20" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | toto     | toto          | tata     |

    Scenario: Link 2 users to a line
        Given I only have the following users:
            | id  | firstname | lastname  |
            | 1   | Greg      | Sanderson |
            | 2   | Cédric    | Abunar    |
        Given I only have the following lines:
            | id | context     | protocol | device_slot |
            | 10 | default     | sip      | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |

        When I create the following links:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "201"
        Then I get a response with a link to the "user_links" resource
        Then I get a response with the following link resources:
            | resource   | id  |
            | users      | 1   |
            | lines      | 10  |
            | extensions | 100 |

        When I create the following links:
            | user_id | line_id | extension_id |
            | 2       | 10      | 100          |
        Then I get a response with status "201"
        Then I get a response with a link to the "user_links" resource
        Then I get a response with the following link resources:
            | resource   | id  |
            | users      | 2   |
            | lines      | 10  |
            | extensions | 100 |

    Scenario: Link a user already associated to a line
        Given I only have the following users:
            | id  | firstname | lastname  |
            | 1   | Greg      | Sanderson |
        Given I only have the following lines:
            | id | context     | protocol | device_slot |
            | 10 | default     | sip      | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |

        When I create the following links:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "201"
        When I create the following links:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: user is already associated to this line"

    Scenario: Provision a device for 2 users
        Given I only have the following users:
            | id  | firstname | lastname  |
            | 1   | Greg      | Sanderson |
            | 2   | Cédric    | Abunar    |
        Given I only have the following lines:
            | id | context     | protocol | username | secret | device_slot |
            | 10 | default     | sip      | abc123   | def456 | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        Given I only have the following devices:
            | id | ip       | mac               |
            | 20 | 10.0.0.1 | 00:00:00:00:00:00 |
        When I create the following links:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
            | 2       | 10      | 100          |
        When I provision my device with my line_id "10" and ip "10.0.0.1"
        Then the device "20" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | abc123   | abc123        | def456   |

    Scenario: Link a second user after provisioning a device
        Given I only have the following users:
            | id  | firstname | lastname  |
            | 1   | Greg      | Sanderson |
            | 2   | Cédric    | Abunar    |
        Given I only have the following lines:
            | id | context     | protocol | username | secret | device_slot |
            | 10 | default     | sip      | abc123   | def456 | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        Given I only have the following devices:
            | id | ip       | mac               |
            | 20 | 10.0.0.1 | 00:00:00:00:00:00 |

        When I create the following links:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "201"
        When I provision my device with my line_id "10" and ip "10.0.0.1"
        Then the device "20" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | abc123   | abc123        | def456   |

        When I create the following links:
            | user_id | line_id | extension_id |
            | 2       | 10      | 100          |
        Then I get a response with status "201"
        Then the device "20" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | abc123   | abc123        | def456   |

    Scenario: Create a link with a provision device and update user callerid
        Given I only have the following users:
            | id | firstname | lastname  |
            | 1  | Greg      | Sanderson |
        Given I only have the following lines:
            | id | context | protocol | username | secret | device_slot |
            | 10 | default | sip      | toto     | tata   | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        Given I only have the following devices:
            | id | ip       | mac               |
            | 20 | 10.0.0.1 | 00:00:00:00:00:00 |
        When I create the following links:
            | user_id | line_id | extension_id |
            | 1       | 10      | 100          |
        Then I get a response with status "201"

        Then I get a response with a link to the "user_links" resource
        Then I get a response with a link to the "extensions" resource with id "100"
        Then I get a response with a link to the "lines" resource with id "10"
        Then I get a response with a link to the "users" resource with id "1"
        Then I get a header with a location for the "user_links" resource
        
        When I provision my device with my line_id "10" and ip "10.0.0.1"
        Then the device "20" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | toto     | toto          | tata     |
        When I update the user with id "1" using the following parameters:
            | firstname | lastname  |
            | Gregory   | Sanderson |
        Then the device "20" has been provisioned with a configuration:
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
            | id  | firstname | lastname  |
            | 1   | Greg      | Sanderson |
            | 2   | Cédric    | Abunar    |
        Given I only have the following lines:
            | id | context     | protocol | username | secret | device_slot |
            | 10 | default     | sip      | toto     | tata   | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |

        When I create the following links:
            | id | user_id | line_id | extension_id |
            | 1  | 1       | 10      | 100          |
            | 2  | 2       | 10      | 100          |
        Then I get a response with status "201"

        When I delete the following links:
            | id |
            | 2  |
        Then I get a response with status "204"

    Scenario: Delete a secondary user after provisioning a device
        Given I only have the following users:
            | id  | firstname | lastname  |
            | 1   | Greg      | Sanderson |
            | 2   | Cédric    | Abunar    |
        Given I only have the following lines:
            | id | context     | protocol | username | secret | device_slot |
            | 10 | default     | sip      | toto     | tata   | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        Given I only have the following devices:
            | id | ip       | mac               |
            | 20 | 10.0.0.1 | 00:00:00:00:00:00 |

        When I create the following links:
            | id | user_id | line_id | extension_id |
            | 1  | 1       | 10      | 100          |
            | 2  | 2       | 10      | 100          |
        Then I get a response with status "201"

        When I provision my device with my line_id "10" and ip "10.0.0.1"
        Then the device "20" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | toto     | toto          | tata     |

        When I delete the following links:
            | id |
            | 2  |
        Then I get a response with status "204"
        Then the device "20" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | toto     | toto          | tata     |

    Scenario: Delete main user
        Given I only have the following users:
            | id  | firstname | lastname  |
            | 1   | Greg      | Sanderson |
            | 2   | Cédric    | Abunar    |
        Given I only have the following lines:
            | id | context     | protocol | username | secret | device_slot |
            | 10 | default     | sip      | toto     | tata   | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |

        When I create the following links:
            | id | user_id | line_id | extension_id |
            | 1  | 1       | 10      | 100          |
            | 2  | 2       | 10      | 100          |
        Then I get a response with status "201"

        When I delete the following links:
            | id |
            | 1  |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: There are secondary users associated to this link"

    Scenario: Delete main user after provisioning a device still has a secondary user
        Given I only have the following users:
            | id  | firstname | lastname  |
            | 1   | Greg      | Sanderson |
            | 2   | Cédric    | Abunar    |
        Given I only have the following lines:
            | id | context     | protocol | username | secret | device_slot |
            | 10 | default     | sip      | toto     | tata   | 1           |
        Given I only have the following extensions:
            | id  | context | exten |
            | 100 | default | 1000  |
        Given I only have the following devices:
            | id | ip       | mac               |
            | 20 | 10.0.0.1 | 00:00:00:00:00:00 |

        When I create the following links:
            | id | user_id | line_id | extension_id |
            | 1  | 1       | 10      | 100          |
            | 2  | 2       | 10      | 100          |

        When I provision my device with my line_id "10" and ip "10.0.0.1"
        Then the device "20" has been provisioned with a configuration:
            | display_name   | number | username | auth_username | password |
            | Greg Sanderson | 1000   | toto     | toto          | tata     |

        When I delete the following links:
            | id |
            | 1  |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: There are secondary users associated to this link"
