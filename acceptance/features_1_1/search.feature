Feature: Filter resources

    Scenario Outline: Pass invalid parameters
        When I request a list for "<resource>" using parameters:
            | name  | value |
            | order | toto  |
        Then I get a response 400 matching "Input Error - order: column 'toto' was not found"

        When I request a list for "<resource>" using parameters:
            | name      | value |
            | direction | toto  |
        Then I get a response 400 matching "Input Error - Direction 'toto' invalid \(must be 'asc' or 'desc'\)"

        When I request a list for "<resource>" using parameters:
            | name  | value |
            | limit | -32   |
        Then I get a response 400 matching "Input Error - Wrong type for 'limit'. Expecting a positive number"

        When I request a list for "<resource>" using parameters:
            | name  | value |
            | limit | asdf  |
        Then I get a response 400 matching "Input Error - Wrong type for 'limit'. Expecting a positive number"

        When I request a list for "<resource>" using parameters:
            | name | value |
            | skip | asdf  |
        Then I get a response 400 matching "Input Error - Wrong type for 'skip'. Expecting a positive number"

        When I request a list for "<resource>" using parameters:
            | name | value |
            | skip | -32   |
        Then I get a response 400 matching "Input Error - Wrong type for 'skip'. Expecting a positive number"

    Examples:
        | resource   |
        | extensions |
        | voicemails |
        | devices    |
        | func_keys  |
        | users      |

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
        | extensions | 120            | 1200            | {"exten": "1200", "context": "default"}                                            | {"exten": "1201", "context": "from-extern"}                                           |
        | extensions | e              | default         | {"exten": "1200", "context": "default"}                                            | {"exten": "1200", "context": "from-extern"}                                           |
        | voicemails | 100            | 1000            | {"number": "1000", "context": "default", "name": "abcd"}                           | {"number": "1001", "context": "default", "name": "abc"}                               |
        | voicemails | abc            | abcd            | {"number": "1000", "context": "default", "name": "abcd"}                           | {"number": "1001", "context": "from-extern", "name": "abc"}                           |
        | voicemails | example.com    | a@example.com   | {"number": "1000", "context": "default", "name": "abcd", "email": "a@example.com"} | {"number": "1001", "context": "from-extern", "name": "abc", "email": "b@example.com"} |
        | devices    | 11             | 00:11           | {"mac": "00:11:22:33:44:55", "ip": "10.0.0.1"}                                     | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"}                                        |
        | devices    | 10             | 10.0            | {"mac": "00:11:22:33:44:55", "ip": "10.0.0.1"}                                     | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"}                                        |
        | users      | john           | Johnny          | {"firstname": "Johnny", "lastname": "Depp"}                                        | {"firstname": "John", "lastname": "Meiers"}                                           |
        | users      | bangoura       | bangourabe      | {"firstname": "Fode", "lastname": "Bangourabe"}                                    | {"firstname": "Jean", "lastname": "Bangoura"}                                         |

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
        | extensions | exten     | {"exten": "1000", "context": "default"}                                           | {"exten": "1001", "context": "from-extern"}                                       |
        | extensions | context   | {"exten": "1100", "context": "default"}                                           | {"exten": "1101", "context": "from-extern"}                                       |
        | voicemails | number    | {"number": "1000", "context": "default", "name": "abc"}                           | {"number": "1001", "context": "default", "name": "def"}                           |
        | voicemails | name      | {"number": "1000", "context": "default", "name": "abc"}                           | {"number": "1001", "context": "default", "name": "def"}                           |
        | voicemails | context   | {"number": "1000", "context": "default", "name": "abc"}                           | {"number": "1001", "context": "from-extern", "name": "def"}                       |
        | voicemails | email     | {"number": "1000", "context": "default", "name": "abc", "email": "a@example.com"} | {"number": "1001", "context": "default", "name": "def", "email": "b@example.com"} |
        | voicemails | language  | {"number": "1000", "context": "default", "name": "abc", "language": "en_US"}      | {"number": "1001", "context": "default", "name": "def", "language": "fr_FR"}      |
        | devices    | mac       | {"mac": "00:11:22:33:44:55", "ip": "10.0.0.1"}                                    | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"}                                    |
        | devices    | ip        | {"mac": "00:11:22:33:44:55", "ip": "10.0.0.1"}                                    | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"}                                    |
        | users      | firstname | {"firstname": "Anne", "lastname": "Depp"}                                         | {"firstname": "Bob", "lastname": "Meiers"}                                        |
        | users      | lastname  | {"firstname": "Richard", "lastname": "Anderson"}                                  | {"firstname": "Elmer", "lastname": "Charles"}                                     |

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
        | extensions | {"exten": "1300", "context": "default"}                  | {"exten": "1001", "context": "from-extern"}              |
        | voicemails | {"number": "1300", "context": "default", "name": "1300"} | {"number": "1001", "context": "default", "name": "1001"} |
        | devices    | {"mac": "aa:11:22:33:44:55", "ip": "10.0.0.1"}           | {"mac": "bb:aa:11:bb:22:cc", "ip": "10.1.0.1"}           |
        | users      | {"firstname": "Daphne", "lastname": "Richards"}          | {"firstname": "Tom", "lastname": "Hilgers"}              |

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
        | extensions | exten     | 499    | {"exten": "4998", "context": "default"}                  | {"exten": "4999", "context": "from-extern"}              |
        | voicemails | number    | 999    | {"number": "9998", "context": "default", "name": "9998"} | {"number": "9999", "context": "default", "name": "9999"} |
        | devices    | mac       | 00:    | {"mac": "00:00:00:00:00:00", "ip": "10.0.0.1"}           | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"}           |
        | users      | firstname | aaaaa  | {"firstname": "aaaaabc", "lastname": "Depp"}             | {"firstname": "aaaaade", "lastname": "Meiers"}           |
