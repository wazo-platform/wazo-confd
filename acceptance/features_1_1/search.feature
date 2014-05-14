Feature: Filter resources

    Scenario Outline: Pass invalid parameters
        When I request a list for "<resource>" using the following parameters:
            | order |
            | toto  |
        Then I get a response 400 matching "Invalid parameters: ordering column 'toto' does not exist"

        When I request a list for "<resource>" using the following parameters:
            | direction |
            | toto      |
        Then I get a response 400 matching "Invalid parameters: direction must be asc or desc"

        When I request a list for "<resource>" using the following parameters:
            | limit |
            | -32   |
        Then I get a response 400 matching "Invalid parameters: limit must be a positive integer"

        When I request a list for "<resource>" using the following parameters:
            | limit |
            | asdf  |
        Then I get a response 400 matching "Invalid parameters: limit must be a positive integer"

        When I request a list for "<resource>" using the following parameters:
            | skip |
            | -42  |
        Then I get a response 400 matching "Invalid parameters: skip must be a positive integer"

        When I request a list for "<resource>" using the following parameters:
            | skip |
            | asdf |
        Then I get a response 400 matching "Invalid parameters: skip must be a positive integer"

    Examples:
        | resource   |
        | extensions |
        | voicemails |
        | devices    |
        | func_keys  |
        | users      |

    Scenario Outline: Search a list
        Given I have created the following "<resource>":
            | item          |
            | <first item>  |
            | <second item> |

        When I search "<resource>" for "<generic search>"
        Then I get a response with status "200"
        Then I get a list containing the following items:
            | item          |
            | <first item>  |
            | <second item> |

        When I search "<resource>" for "<specific search>"
        Then I get a response with status "200"
        Then I get a list containing the following items:
            | item         |
            | <first item> |
        Then I get a list that does not contain the following items:
            | item          |
            | <second item> |

    Examples:
        | resource   | first item                                      | second item                                    | generic search | specific search |
        | extensions | {"exten": "1200", "context": "default"}         | {"exten": "1201", "context": "from-extern"}    | 120            | 1200            |
        | extensions | {"exten": "1200", "context": "default"}         | {"exten": "1200", "context": "from-extern"}    | e              | default         |
        | voicemails | {"number": "1000", "context": "default"}        | {"number": "1001", "context": "default"}       | 100            | 1001            |
        | voicemails | {"number": "1000", "context": "default"}        | {"number": "1001", "context": "from-extern"}   | e              | default         |
        | devices    | {"mac": "00:11:22:33:44:55", "ip": "10.0.0.1" } | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"} | 11             | 00:11           |
        | devices    | {"mac": "00:11:22:33:44:55", "ip": "10.0.0.1" } | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"} | 10             | 10.0            |
        | users      | {"firstname": "Johnny", "lastname": "Depp"}     | {"firstname": "John", "lastname": "Meiers"}    | john           | Johnny          |
        | users      | {"firstname": "Fode", "lastname": "Bangourabe"} | {"firstname": "Jean", "lastname": "Bangoura"}  | bangoura       | bangourabe      |

    Scenario Outline: Sort a list using an order and direction
        Given I have created the following "<resource>":
            | item          |
            | <first item>  |
            | <second item> |

        When I request a list for "<resource>" using the following parameters:
            | order    | direction |
            | <column> | asc       |
        Then I get a response with status "200"
        Then I get a list of items in the following order:
            | item          |
            | <first item>  |
            | <second item> |

        When I request a list for "<resource>" using the following parameters:
            | order    | direction |
            | <column> | desc      |
        Then I get a response with status "200"
        Then I get a list of items in the following order:
            | item          |
            | <second item> |
            | <first item>  |

    Examples:
        | resource   | first item                                       | second item                                    | column    |
        | extensions | {"exten": "1000", "context": "default"}          | {"exten": "1001", "context": "from-extern"}    | exten     |
        | extensions | {"exten": "1100", "context": "default"}          | {"exten": "1101", "context": "from-extern"}    | context   |
        | voicemails | {"number": "1000", "context": "default"}         | {"number": "1001", "context": "default"}       | exten     |
        | voicemails | {"number": "1100", "context": "default"}         | {"number": "1101", "context": "from-extern"}   | context   |
        | devices    | {"mac": "00:11:22:33:44:55", "ip": "10.0.0.1" }  | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"} | mac       |
        | devices    | {"mac": "00:11:22:33:44:55", "ip": "10.0.0.1" }  | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"} | ip        |
        | users      | {"firstname": "Anne", "lastname": "Depp"}        | {"firstname": "Bob", "lastname": "Meiers"}     | firstname |
        | users      | {"firstname": "Richard", "lastname": "Anderson"} | {"firstname": "Elmer", "lastname": "Charles"}  | lastname  |

    Scenario Outline: Limit a list
        Given I have created the following "<resource>":
            | item          |
            | <first item>  |
            | <second item> |
        When I request a list for "<resource>" using the following parameters:
            | limit |
            | 1     |
        Then I get a response with status "200"
        Then I have a list with 1 results

    Examples:
        | resource   | first item                                      | second item                                    |
        | extensions | {"exten": "1300", "context": "default"}         | {"exten": "1001", "context": "from-extern"}    |
        | voicemails | {"number": "1300", "context": "default"}        | {"number": "1001", "context": "default"}       |
        | devices    | {"mac": "aa:11:22:33:44:55", "ip": "10.0.0.1" } | {"mac": "bb:aa:11:bb:22:cc", "ip": "10.1.0.1"} |
        | users      | {"firstname": "Daphne", "lastname": "Richards"} | {"firstname": "Tom", "lastname": "Hilgers"}    |

    Scenario Outline: Skip items in a list
        Given I have created the following "<resource>":
            | item          |
            | <first item>  |
            | <second item> |
        When I request a list for "<resource>" using the following parameters:
            | skip | order    |
            | 1    | <column> |
        Then I get a list containing the following items:
            | item          |
            | <second item> |
        Then I do not have the following items in the list:
            | item         |
            | <first item> |

    Examples:
        | resource   | first item                                       | second item                                    | column    |
        | extensions | {"exten": "1000", "context": "default"}          | {"exten": "1001", "context": "from-extern"}    | exten     |
        | voicemails | {"number": "1000", "context": "default"}         | {"number": "1001", "context": "default"}       | exten     |
        | devices    | {"mac": "00:11:22:33:44:55", "ip": "10.0.0.1" }  | {"mac": "00:aa:11:bb:22:cc", "ip": "10.1.0.1"} | mac       |
        | users      | {"firstname": "Aaaaaaaaaaa", "lastname": "Depp"} | {"firstname": "Bob", "lastname": "Meiers"}     | firstname |
