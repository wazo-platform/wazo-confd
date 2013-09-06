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
        Then the device has the following parameters:
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
        Then the device has the following parameters:
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
        Then the device has the following parameters:
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
        Then the device has the following parameters:
            | template_id |
            | abcd1234    |

    Scenario: Create a device with all parameters
        Given there are no devices with mac "00:11:22:33:44:57"
        Given the plugin "null" is installed
        Given there exists the following device templates:
            | id         | label        |
            | mytemplate | testtemplate |
        When I create the following devices:
            | ip       | mac               | plugin | model     | vendor     | version | template_id |
            | 10.0.0.1 | 00:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate  |
        Then I get a response with status "201"
        Then I get a response with a device id
        Then I get a header with a location for the "devices" resource
        Then I get a response with a link to the "devices" resource
        Then the device has the following parameters:
            | ip       | mac               | plugin | model     | vendor     | version | template_id |
            | 10.0.0.1 | 00:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate  |

    Scenario: Get a device that doesn't exist
        Given there are no devices with id "1234567890abcdefghij1234567890ab"
        When I go get the device with id "1234567890abcdefghij1234567890ab"
        Then I get a response with status "404"

    Scenario: Get a device that exists
        Given there exists the following device templates:
            | id         | label       |
            | mytemplate | My Template |
        Given the plugin "null" is installed
        Given I have the following devices:
            | ip       | mac               | plugin | model     | vendor     | version | template_id |
            | 10.0.0.1 | 00:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate  |
        When I go get the device with id "1234567890abcdefghij1234567890ab"
        Then I get a response with status "201"
        Then I get a response with a link to the "devices" resource
        Then the device has the following parameters:
            | ip       | mac               | plugin | model     | vendor     | version | template_id |
            | 10.0.0.1 | 00:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate  |

    Scenario: Device list with minimum 2 devices
        Given there exists the following device templates:
            | id         | label       |
            | mytemplate | My Template |
        Given the plugin "null" is installed
        Given I have the following devices:
            | ip       | mac               | plugin | model     | vendor     | version | template_id         |
            | 10.0.0.1 | 00:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate          |
            | 10.0.0.2 | 00:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
        When I access the list of devices
        Then I get a response with status "200"
        Then I get a list containing the following devices:
            | ip       | mac               | plugin | model     | vendor     | version | template_id         |
            | 10.0.0.1 | 00:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate          |
            | 10.0.0.2 | 00:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
        Then the list contains the same number of devices as on the provisioning server

    Scenario: Sorted device list
        Given there exists the following device templates:
            | id         | label       |
            | mytemplate | My Template |
        Given the plugin "null" is installed
        Given I have the following devices:
            | ip       | mac               | plugin | model     | vendor     | version | template_id         |
            | 10.0.0.1 | 22:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate          |
            | 10.0.0.2 | aa:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
            | 10.0.0.3 | 00:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
        When I request a list of devices with the following query parameters:
            | sort | order |
            | ip   | desc  |
        Then I get a response with status "200"
        Then I get a list of devices in the following order:
            | ip       | mac               | plugin | model     | vendor     | version | template_id         |
            | 10.0.0.3 | 00:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
            | 10.0.0.2 | aa:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
            | 10.0.0.1 | 22:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate          |
        When I request a list of devices with the following query parameters:
            | sort | order |
            | mac  | asc   |
        Then I get a response with status "200"
        Then I get a list of devices in the following order:
            | ip       | mac               | plugin | model     | vendor     | version | template_id         |
            | 10.0.0.3 | 00:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
            | 10.0.0.1 | 22:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate          |
            | 10.0.0.2 | aa:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |

    Scenario: Paginated device list
        Given I only have 15 devices
        When I request a list of devices with the following query parameters:
            | limit |
            | 10    |
        Then I get a response with status "200"
        Then I get a list with 10 devices
        When I request a list of devices with the following query parameters:
            | limit | skip |
            | 10    | 10   |
        Then I get a response with status "200"
        Then I get a list with 5 devices

    Scenario: Device list ordered and paginated
        Given there exists the following device templates:
            | id         | label       |
            | mytemplate | My Template |
        Given the plugin "null" is installed
        Given I have the following devices:
            | ip       | mac               | plugin | model     | vendor     | version | template_id         |
            | 10.0.0.1 | 22:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate          |
            | 10.0.0.2 | aa:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
            | 10.0.0.3 | 00:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
        When I request a list of devices with the following query parameters:
            | sort | order  | limit | skip |
            | ip   | desc   | 2     | 1    |
        Then I get a response with status "200"
        Then I get a list of devices in the following order:
            | ip       | mac               | plugin | model     | vendor     | version | template_id         |
            | 10.0.0.2 | aa:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
            | 10.0.0.1 | 22:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate          |
