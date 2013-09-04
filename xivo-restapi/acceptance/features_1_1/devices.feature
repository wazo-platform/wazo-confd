Feature: Devices

    Scenario: Create a device with no parameters
        When I create an empty device
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "devices" resource
        Then I get a response with a link to the "devices" resource

    Scenario: Create a device with one parameter
        When I create the following devices:
            | ip       |
            | 10.0.0.1 |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "devices" resource
        Then I get a response with a link to the "devices" resource
        Then the created device has the following parameters:
            | ip       |
            | 10.0.0.1 |

    Scenario: Create a device with an invalid ip address
        When I create the following devices:
            | ip           | mac               |
            | 10.389.34.21 | 00:11:22:33:44:50 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: ip"
        When I create the following devices:
            | ip            | mac               |
            | 1024.34.34.21 | 00:11:22:33:44:50 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: ip"

    Scenario: Create a device with an invalid mac address
        When I create the following devices:
            | ip       | mac               |
            | 10.0.0.1 | ZZ:11:22:33:44:50 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: mac"
        When I create the following devices:
            | ip       | mac                |
            | 10.0.0.1 | 00:11:22:DF5:44:50 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: mac"
        When I create the following devices:
            | ip       | mac            |
            | 10.0.0.1 | 11:22:33:44:50 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: mac"

    Scenario: Create a device with ip and mac
        When I create the following devices:
            | ip       | mac               |
            | 10.0.0.1 | 00:11:22:33:44:51 |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "devices" resource
        Then I get a response with a link to the "devices" resource
        Then the created device has the following parameters:
            | ip       | mac               | plugin |
            | 10.0.0.1 | 00:11:22:33:44:51 |        |

    Scenario: Create 2 devices with same mac
        When I create the following devices:
            | ip       | mac               |
            | 10.0.0.2 | 00:11:22:33:44:52 |
        Then I get a response with status "201"
        When I create the following devices:
            | ip       | mac               |
            | 10.0.0.3 | 00:11:22:33:44:52 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: mac already exists"

    Scenario: Create 2 devices with the same ip address
        When I create the following devices:
            | ip       | mac               |
            | 10.0.0.4 | 00:11:22:33:44:53 |
        Then I get a response with status "201"
        When I create the following devices:
            | ip       | mac               |
            | 10.0.0.4 | 00:11:22:33:44:54 |
        Then I get a response with status "201"

    Scenario: Create a device with a plugin that doesn't exist
        When I create the following devices:
            | ip       | mac               | plugin                   |
            | 10.0.0.5 | 00:11:22:33:44:55 | mysuperduperplugin-1.2.3 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: plugin does not exist"

    Scenario: Create a device with a plugin
        Given the plugin "null" is installed
        When I create the following devices:
            | ip       | mac               | plugin |
            | 10.0.0.6 | 00:11:22:33:44:56 | null   |
        Then I get a response with status "201"
        Then I get a response with an id
        Then I get a header with a location for the "devices" resource
        Then I get a response with a link to the "devices" resource
        Then the created device has the following parameters:
            | ip       | mac               | plugin |
            | 10.0.0.1 | 00:11:22:33:44:51 | null   |
