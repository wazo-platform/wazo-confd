Feature: Devices

    Scenario: Create a device with no parameters
        When I create an empty device
        Then I get a response with status "201"
        Then I get a response with a device id
        Then I get a header with a location for the "devices" resource
        Then I get a response with a link to the "devices" resource

    Scenario: Create a device with one parameter
        When I create the following devices:
            | ip       |
            | 10.0.0.1 |
        Then I get a response with status "201"
        Then I get a response with a device id
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
        Given there are no devices with mac "00:11:22:33:44:51"
        When I create the following devices:
            | ip       | mac               |
            | 10.0.0.1 | 00:11:22:33:44:51 |
        Then I get a response with status "201"
        Then I get a response with a device id
        Then I get a header with a location for the "devices" resource
        Then I get a response with a link to the "devices" resource
        Then the created device has the following parameters:
            | ip       | mac               |
            | 10.0.0.1 | 00:11:22:33:44:51 |

    Scenario: Create 2 devices with same mac
        Given there are no devices with mac "00:11:22:33:44:52"
        When I create the following devices:
            | ip       | mac               |
            | 10.0.0.2 | 00:11:22:33:44:52 |
        Then I get a response with status "201"
        When I create the following devices:
            | ip       | mac               |
            | 10.0.0.3 | 00:11:22:33:44:52 |
        Then I get a response with status "400"
        Then I get an error message "device 00:11:22:33:44:52 already exists"

    Scenario: Create 2 devices with the same ip address
        Given there are no devices with mac "00:11:22:33:44:53"
        Given there are no devices with mac "00:11:22:33:44:54"
        When I create the following devices:
            | ip       | mac               |
            | 10.0.0.4 | 00:11:22:33:44:53 |
        Then I get a response with status "201"
        When I create the following devices:
            | ip       | mac               |
            | 10.0.0.4 | 00:11:22:33:44:54 |
        Then I get a response with status "201"

    Scenario: Create a device with a plugin that doesn't exist
        Given there are no devices with mac "00:11:22:33:44:55" 
        When I create the following devices:
            | ip       | mac               | plugin                   |
            | 10.0.0.5 | 00:11:22:33:44:55 | mysuperduperplugin-1.2.3 |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: plugin mysuperduperplugin-1.2.3 does not exist"

    Scenario: Create a device with a plugin
        Given there are no devices with mac "00:11:22:33:44:56"
        Given the plugin "null" is installed
        When I create the following devices:
            | ip       | mac               | plugin |
            | 10.0.0.6 | 00:11:22:33:44:56 | null   |
        Then I get a response with status "201"
        Then I get a response with a device id
        Then I get a header with a location for the "devices" resource
        Then I get a response with a link to the "devices" resource
        Then the created device has the following parameters:
            | ip       | mac               | plugin |
            | 10.0.0.6 | 00:11:22:33:44:56 | null   |

    Scenario: Create a device with a config template that doesn't exist
        When I create a device using the device template id "mysuperduperdevicetemplate"
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: template_id mysuperduperdevicetemplate does not exist"

    Scenario: Create a device with a config template
        Given there exists the following device templates:
            | id       | label        |
            | abcd1234 | testtemplate |
        When I create a device using the device template id "abcd1234"
        Then I get a response with status "201"
        Then I get a response with a device id
        Then I get a header with a location for the "devices" resource
        Then I get a response with a link to the "devices" resource
        Then the created device has the following parameters:
            | template_id |
            | abcd1234    |

    Scenario: Synchronize a device
        Given there are no devices with id "123"
        Given there are no devices with mac "00:00:00:00:aa:01"
        Given I have the following devices:
          | id  | ip             | mac               |
          | 123 | 192.168.32.197 | 00:00:00:00:aa:01 |
        When I synchronize the device "123" from restapi
        Then I see in the log file device "123" synchronized

    Scenario: Reset to autoprov a device
        Given there are no devices with id "123"
        Given there are no devices with mac "00:00:00:00:aa:01"
        Given I have the following devices:
          | id  | ip             | mac               |
          | 123 | 192.168.32.197 | 00:00:00:00:aa:01 |
        When I reset the device "123" to autoprov from restapi
        Then I see in the log file device "123" autoprovisioned
        