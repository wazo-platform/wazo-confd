Feature: REST API Devices

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
        Given there are no devices with mac "00:11:22:33:44:55"
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

    Scenario: Synchronize a device
        Given there are no devices with id "123"
        Given there are no devices with mac "00:00:00:00:aa:01"
        Given I have the following devices:
          | id  | ip             | mac               |
          | 123 | 192.168.32.197 | 00:00:00:00:aa:01 |
        When I synchronize the device "123" from restapi
        Then I see in the log file device "123" synchronized

    Scenario: Edit a device with no parameters
        Given I have the following devices:
            | ip       | mac               |
            | 10.0.0.1 | 00:11:22:33:44:55 |
        When I edit the device with mac "00:11:22:33:44:55" using no parameters
        Then I get a response with status "204"
        When I go get the device with mac "00:11:22:33:44:55" using its id
        Then I get a response with status "200"
        Then the device has the following parameters:
            | ip       | mac               |
            | 10.0.0.1 | 00:11:22:33:44:55 |

    Scenario: Edit a device with ip and mac
        Given I have the following devices:
            | ip       | mac               |
            | 10.0.0.1 | 00:11:22:33:44:55 |
        When I edit the device with mac "00:11:22:33:44:55" using the following parameters:
            | ip       | mac               |
            | 10.0.0.2 | 00:11:22:33:44:55 |
        Then I get a response with status "204"
        When I go get the device with mac "00:11:22:33:44:55" using its id
        Then I get a response with status "200"
        Then the device has the following parameters:
            | ip | mac               |
            | 10.0.0.2 | 00:11:22:33:44:55 |

    Scenario: Edit a device by adding new parameters
        Given the plugin "null" is installed
        Given there exists the following device templates:
            | id         | label        |
            | mytemplate | testtemplate |
        Given there are no devices with mac "aa:11:22:33:44:55"
        Given I have the following devices:
            | mac               |
            | 00:11:22:33:44:55 |
        When I edit the device with mac "00:11:22:33:44:55" using the following parameters:
            | ip       | mac               | plugin | model     | vendor     | version | template_id |
            | 10.1.0.1 | aa:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate  |
        Then I get a response with status "204"
        When I go get the device with mac "aa:11:22:33:44:55" using its id
        Then I get a response with status "200"
        Then the device has the following parameters:
            | ip       | mac               | plugin | model     | vendor     | version | template_id |
            | 10.1.0.1 | aa:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate  |

    Scenario: Edit a device with an invalid mac
        Given I have the following devices:
            | mac               |
            | 00:11:22:33:44:55 |
        When I edit the device with mac "00:11:22:33:44:55" using the following parameters:
            | mac               |
            | ZZ:11:22:33:44:56 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: mac"
        When I edit the device with mac "00:11:22:33:44:55" using the following parameters:
            | mac                |
            | aa:110:22:33:44:56 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: mac"

    Scenario: Edit a device with a mac that already exists
        Given I have the following devices:
            | mac               |
            | 00:11:22:33:44:55 |
            | 00:11:22:33:44:56 |
        When I edit the device with mac "00:11:22:33:44:55" using the following parameters:
            | mac               |
            | 00:11:22:33:44:56 |
        Then I get a response with status "400"
        Then I get an error message "device 00:11:22:33:44:56 already exists"

    Scenario: Edit a device with an invalid ip
        Given I have the following devices:
            | mac               | ip       |
            | 00:11:22:33:44:55 | 10.0.0.1 |
        When I edit the device with mac "00:11:22:33:44:55" using the following parameters:
            | ip        |
            | 399.0.0.1 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: ip"
        When I edit the device with mac "00:11:22:33:44:55" using the following parameters:
            | ip          |
            | 10.9999.0.1 |
        Then I get a response with status "400"
        Then I get an error message "Invalid parameters: ip"

    Scenario: Edit a device with a template that does not exist
        Given I have the following devices:
            | mac               |
            | 00:11:22:33:44:55 |
        When I edit the device with mac "00:11:22:33:44:55" using the following parameters:
            | template_id          |
            | mysuperdupertemplate |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: template_id mysuperdupertemplate does not exist"

    Scenario: Edit a device with a custom template
        Given there exists the following device templates:
            | id            | label          |
            | testtemplate  | Test Template  |
            | supertemplate | Super Template |
        Given I have the following devices:
            | mac               | template_id  |
            | 00:11:22:33:44:55 | testtemplate |
        When I edit the device with mac "00:11:22:33:44:55" using the following parameters:
            | template_id   |
            | supertemplate |
        Then I get a response with status "204"
        When I go get the device with mac "00:11:22:33:44:55" using its id
        Then I get a response with status "200"
        Then the device has the following parameters:
            | mac               | template_id   |
            | 00:11:22:33:44:55 | supertemplate |

    Scenario: Edit a device with a plugin that does not exist
        Given I have the following devices:
            | mac               |
            | 00:11:22:33:44:55 |
        When I edit the device with mac "00:11:22:33:44:55" using the following parameters:
            | plugin          |
            | mysuperplugin   |
        Then I get a response with status "400"
        Then I get an error message "Nonexistent parameters: plugin mysuperplugin does not exist"

    Scenario: Edit a device with a plugin
        Given the plugin "null" is installed
        Given the plugin "xivo-aastra-switchboard" is installed
        Given I have the following devices:
            | mac               | plugin |
            | 00:11:22:33:44:55 | null   |
        When I edit the device with mac "00:11:22:33:44:55" using the following parameters:
            | plugin                  |
            | xivo-aastra-switchboard |
        Then I get a response with status "204"
        When I go get the device with mac "00:11:22:33:44:55" using its id
        Then I get a response with status "200"
        Then the device has the following parameters:
            | mac               | plugin                  |
            | 00:11:22:33:44:55 | xivo-aastra-switchboard |

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
        When I go get the device with mac "00:11:22:33:44:55" using its id
        Then I get a response with status "200"
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
        When I request the list of devices
        Then I get a response with status "200"
        Then I get a list containing the following devices:
            | ip       | mac               | plugin | model     | vendor     | version | template_id         |
            | 10.0.0.1 | 00:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate          |
            | 10.0.0.2 | 00:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
        Then the list contains the same number of devices as on the provisioning server

    Scenario: Search for a device
        Given I have the following devices:
            | ip       | mac               | plugin | model     | version |
            | 10.0.0.1 | 00:11:22:33:ab:55 | null   | nullmodel | 1.0     |
            | 10.0.0.2 | 00:11:22:33:cd:56 | null   | nullmodel | 1.0     |
        When I request a list of devices with the following query parameters:
            | search   |
            | 33:AB:55 |
        Then I get a response with status "200"
        Then I get a list containing the following devices:
            | ip       | mac               | plugin | model     | version |
            | 10.0.0.1 | 00:11:22:33:ab:55 | null   | nullmodel | 1.0     |
        Then I get a list with 1 of 1 devices

    Scenario: Search for a device with pagination
        Given I have the following devices:
            | ip       | mac               | plugin | model     | version |
            | 10.1.0.1 | 00:11:22:33:cd:56 | null   | nullmodel | 1.0     |
            | 10.1.0.2 | 00:11:22:33:cd:57 | null   | nullmodel | 1.0     |
            | 10.0.0.1 | 00:11:22:33:ab:55 | null   | nullmodel | 1.0     |
            | 10.1.0.3 | 00:11:22:33:cd:58 | null   | nullmodel | 1.0     |
        When I request a list of devices with the following query parameters:
            | search | limit | skip | order | direction |
            |   10.1 |     2 |    1 | ip    | asc       |
        Then I get a response with status "200"
        Then I get a list containing the following devices:
            | ip       | mac               | plugin | model     | version |
            | 10.1.0.2 | 00:11:22:33:cd:57 | null   | nullmodel | 1.0     |
            | 10.1.0.3 | 00:11:22:33:cd:58 | null   | nullmodel | 1.0     |
        Then I get a list with 2 of 3 devices

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
            | order | direction |
            | ip    | desc      |
        Then I get a response with status "200"
        Then I get a list of devices in the following order:
            | ip       | mac               | plugin | model     | vendor     | version | template_id         |
            | 10.0.0.3 | 00:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
            | 10.0.0.2 | aa:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
            | 10.0.0.1 | 22:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate          |
        When I request a list of devices with the following query parameters:
            | order | direction |
            | mac   | asc       |
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
        Then I get a list with 5 of 15 devices

    Scenario: Device list ordered and paginated
        Given there exists the following device templates:
            | id         | label       |
            | mytemplate | My Template |
        Given the plugin "null" is installed
        Given I have the following devices:
            | ip              | mac               | plugin | model     | vendor     | version | template_id         |
            | 255.255.255.251 | 22:11:22:33:44:55 | null   | nullmodel | nullvendor | 1.0     | mytemplate          |
            | 255.255.255.252 | aa:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
            | 255.255.255.253 | 00:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
            | 255.255.255.254 | bb:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
        When I request a list of devices with the following query parameters:
            | order | direction | limit | skip |
            | ip    | desc      | 2     | 1    |
        Then I get a response with status "200"
        Then I get a list of devices in the following order:
            | ip              | mac               | plugin | model     | vendor     | version | template_id         |
            | 255.255.255.253 | 00:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
            | 255.255.255.252 | aa:11:22:33:44:56 | null   | nullmodel | nullvendor | 1.0     | defaultconfigdevice |
        Then I get a list with 2 devices

    Scenario: Reset to autoprov a device
        Given there are no devices with id "123"
        Given there are no devices with mac "00:00:00:00:aa:01"
        Given I have the following devices:
          | id  | ip             | mac               |
          | 123 | 192.168.32.197 | 00:00:00:00:aa:01 |
        When I reset the device "123" to autoprov from restapi
        Then I see in the log file device "123" autoprovisioned

    Scenario: Associate line to a device
        Given I only have the following lines:
            | id | context | protocol | username | secret | device_slot |
            | 10 | default | sip      | toto     | tata   | 1           |
        Given I only have the following devices:
            | id | ip       | mac               |
            | 20 | 10.0.0.1 | 00:00:00:00:00:12 |
        When I associate my line_id "10" to the device "20"
        Then I get a response with status "403"

    Scenario: Remove line to a device
        Given I only have the following lines:
            | id | context | protocol | username | secret | device_slot |
            | 10 | default | sip      | toto     | tata   | 1           |

        When I remove line_id "10" from device "20"
        Then I get a response with status "403"

    Scenario: Delete a device
        Given I only have the following devices:
            | id | ip       | mac               |
            | 20 | 10.0.0.1 | 00:00:00:00:00:12 |
        When I delete the device "20" from restapi
        Then I get a response with status "204"
        Then I see in the log file device "20" deleted
        Then the device "20" is no longer exists in provd

    Scenario: Delete a device that doesn't exist
        Given there are no devices with id "abcd"
        When I delete the device "abcd" from restapi
        Then I get a response with status "404"
