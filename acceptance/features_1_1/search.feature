Feature: Filter resources

    Scenario Outline: Pass invalid parameters
        When I request a list for "<resource>" using parameters:
            | name  | value |
            | order | toto  |
        Then I get a response 400 matching "Invalid parameters: ordering column 'toto' does not exist"

        When I request a list for "<resource>" using parameters:
            | name      | value |
            | direction | toto  |
        Then I get a response 400 matching "Invalid parameters: direction must be asc or desc"

        When I request a list for "<resource>" using parameters:
            | name  | value |
            | limit | -32   |
        Then I get a response 400 matching "Invalid parameters: limit must be a positive integer"

        When I request a list for "<resource>" using parameters:
            | name  | value |
            | limit | asdf  |
        Then I get a response 400 matching "Invalid parameters: limit must be a positive integer"

        When I request a list for "<resource>" using parameters:
            | name | value |
            | skip | asdf  |
        Then I get a response 400 matching "Invalid parameters: skip must be a positive integer"

        When I request a list for "<resource>" using parameters:
            | name | value |
            | skip | -32   |
        Then I get a response 400 matching "Invalid parameters: skip must be a positive integer"

    Examples:
        | resource   |
        | voicemails |
        | devices    |
        | func_keys  |

    Scenario Outline: Search a list
        Given I have the following "<resource>":
            | item          |
            | <first item>  |
            | <second item> |

        When I request a list for "<resource>" using parameters:
            | name   | value            |
            | search | <generic search> |
        Then I get a list containing the following items:
            | item          |
            | <first item>  |
            | <second item> |

        When I request a list for "<resource>" using parameters:
            | name   | value             |
            | search | <specific search> |
        Then I get a list containing the following items:
            | item         |
            | <first item> |
        Then I get a list that does not contain the following items:
            | item          |
            | <second item> |

    Examples:
        | resource   | generic search | specific search | first item                                                                         | second item                                                                           |
        | voicemails | 100            | 1000            | {"number": "1000", "context": "default", "name": "abcd"}                           | {"number": "1001", "context": "default", "name": "abc"}                               |
        | voicemails | abc            | abcd            | {"number": "1000", "context": "default", "name": "abcd"}                           | {"number": "1001", "context": "from-extern", "name": "abc"}                           |
        | voicemails | example.com    | a@example.com   | {"number": "1000", "context": "default", "name": "abcd", "email": "a@example.com"} | {"number": "1001", "context": "from-extern", "name": "abc", "email": "b@example.com"} |
        | devices    | 11             | 00:11           | {"mac": "00:11:22:33:44:55", "ip": "10.0.0.1"}                                     | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"}                                        |
        | devices    | 10             | 10.0            | {"mac": "00:11:22:33:44:55", "ip": "10.0.0.1"}                                     | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"}                                        |

    Scenario Outline: Sort a list using an order and direction
        Given I have the following "<resource>":
            | item          |
            | <first item>  |
            | <second item> |

        When I request a list for "<resource>" using parameters:
            | name      | value    |
            | order     | <column> |
            | direction | asc      |
        Then I get a list of items in the following order:
            | item          |
            | <first item>  |
            | <second item> |

        When I request a list for "<resource>" using parameters:
            | name      | value    |
            | order     | <column> |
            | direction | desc     |
        Then I get a list of items in the following order:
            | item          |
            | <second item> |
            | <first item>  |

    Examples:
        | resource   | column    | first item                                                                        | second item                                                                       |
        | voicemails | number    | {"number": "1000", "context": "default", "name": "abc"}                           | {"number": "1001", "context": "default", "name": "def"}                           |
        | voicemails | name      | {"number": "1000", "context": "default", "name": "abc"}                           | {"number": "1001", "context": "default", "name": "def"}                           |
        | voicemails | context   | {"number": "1000", "context": "default", "name": "abc"}                           | {"number": "1001", "context": "from-extern", "name": "def"}                       |
        | voicemails | email     | {"number": "1000", "context": "default", "name": "abc", "email": "a@example.com"} | {"number": "1001", "context": "default", "name": "def", "email": "b@example.com"} |
        | voicemails | language  | {"number": "1000", "context": "default", "name": "abc", "language": "en_US"}      | {"number": "1001", "context": "default", "name": "def", "language": "fr_FR"}      |
        | devices    | mac       | {"mac": "00:11:22:33:44:55", "ip": "10.0.0.1"}                                    | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"}                                    |
        | devices    | ip        | {"mac": "00:11:22:33:44:55", "ip": "10.0.0.1"}                                    | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"}                                    |

    Scenario Outline: Limit a list
        Given I have the following "<resource>":
            | item          |
            | <first item>  |
            | <second item> |
        When I request a list for "<resource>" using parameters:
            | name  | value |
            | limit | 1     |
        Then I have a list with 1 results

    Examples:
        | resource   | first item                                               | second item                                              |
        | voicemails | {"number": "1300", "context": "default", "name": "1300"} | {"number": "1001", "context": "default", "name": "1001"} |
        | devices    | {"mac": "aa:11:22:33:44:55", "ip": "10.0.0.1"}           | {"mac": "bb:aa:11:bb:22:cc", "ip": "10.1.0.1"}           |

    Scenario Outline: Skip items in a list
        Given I have the following "<resource>":
            | item          |
            | <first item>  |
            | <second item> |
        When I request a list for "<resource>" using parameters:
            | name   | value    |
            | skip   | 1        |
            | order  | <column> |
            | search | <search> |
        Then I get a list containing the following items:
            | item          |
            | <second item> |
        Then I get a list that does not contain the following items:
            | item         |
            | <first item> |

    Examples:
        | resource   | column    | search | first item                                               | second item                                              |
        #| extensions | exten     | 100    | {"exten": "1000", "context": "default"}                  | {"exten": "1001", "context": "from-extern"}              |
        | voicemails | number    | 100    | {"number": "1000", "context": "default", "name": "1000"} | {"number": "1001", "context": "default", "name": "1001"} |
        | devices    | mac       | 00:    | {"mac": "00:00:00:00:00:00", "ip": "10.0.0.1"}           | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"}           |
        #| users      | firstname | aaaaa  | {"firstname": "aaaaabc", "lastname": "Depp"}             | {"firstname": "aaaaade", "lastname": "Meiers"}           |

    Scenario Outline: Paginated Search
        Given I have the following "<resource>":
            | item           |
            | <first item>   |
            | <second item>  |
            | <skipped item> |
            | <missing item> |
        When I request a list for "<resource>" using parameters:
            | name      | value    |
            | search    | <search> |
            | skip      | 1        |
            | limit     | 2        |
            | order     | <column> |
            | direction | desc     |
        Then I get a list containing the following items:
            | item          |
            | <second item> |
            | <first item>  |
        Then I get a list that does not contain the following items:
            | item           |
            | <missing item> |
            | <skipped item> |

    Examples:
        | resource   | search | column | first item                                               | second item                                              | skipped item                                             | missing item                                             |
        | voicemails | 123    | number | {"number": "1231", "context": "default", "name": "1231"} | {"number": "1232", "context": "default", "name": "1232"} | {"number": "1233", "context": "default", "name": "1233"} | {"number": "1412", "context": "default", "name": "1412"} |
        | devices    | 00:ff  | mac    | {"mac": "00:ff:01:00:00:00"}                             | {"mac": "00:ff:02:00:00:00"}                             | {"mac": "00:ff:03:00:00:00"}                             | {"mac": "00:f1:00:00:00:00"}                             |
