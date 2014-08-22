Feature: REST API Call logs consultation

    Scenario: List call logs
        Given there are only the following call logs:
          | date                | source_name | source_exten | destination_exten | duration | user_field | answered |
          | 2013-01-30 08:46:20 | Père Noël   |         1009 |              1001 |  0:00:03 |            | True     |
          | 2013-01-30 11:03:47 | Bob Marley  |         1002 |        4185550155 |  0:00:00 |            | False    |
          | 2013-01-30 11:20:08 | Bob Marley  |         1002 |        4185550155 |  0:00:03 | Père Noël  | True     |
        When I get the list of call logs
        Then I get the following call logs in CSV format:
          | Call Date           | Caller            |     Called | Period | user Field |
          | 2013-01-30T08:46:20 | Père Noël (1009)  |       1001 |      3 |            |
          | 2013-01-30T11:03:47 | Bob Marley (1002) | 4185550155 |      0 |            |
          | 2013-01-30T11:20:08 | Bob Marley (1002) | 4185550155 |      3 | Père Noël  |

    Scenario: List call logs with CSV separator inside fields
        Given there are only the following call logs:
          | date                | source_name | source_exten | destination_exten | duration | user_field | answered |
          | 2013-01-30 08:46:20 | Père, Noël  |         1009 |              1001 |  0:00:03 |            | True     |
          | 2013-01-30 11:03:47 | Bob, Marley |         1002 |        4185550155 |  0:00:00 |            | False    |
          | 2013-01-30 11:20:08 | Bob, Marley |         1002 |        4185550155 |  0:00:03 | Père Noël  | True     |
        When I get the list of call logs
        Then I get the following call logs in CSV format:
          | Call Date           | Caller             |     Called | Period | user Field |
          | 2013-01-30T08:46:20 | Père, Noël (1009)  |       1001 |      3 |            |
          | 2013-01-30T11:03:47 | Bob, Marley (1002) | 4185550155 |      0 |            |
          | 2013-01-30T11:20:08 | Bob, Marley (1002) | 4185550155 |      3 | Père Noël  |

    Scenario: List call logs in a period with start greater than end
        Given there are only the following call logs:
          | date                | source_name | source_exten | destination_exten | duration | user_field | answered |
          | 2013-01-29 08:46:20 | Père Noël   |         1009 |              1001 |  0:00:03 |            | True     |
          | 2013-01-30 11:20:08 | Bob Marley  |         1002 |        4185550155 |  0:00:03 | Père Noël  | True     |
          | 2013-01-31 11:20:08 | Bob Marley  |         1002 |        4185550155 |  0:00:03 | Père Noël  | True     |
        When I get the list of call logs with arguments:
          | start_date          | end_date            |
          | 2013-01-31T00:00:00 | 2013-01-30T00:00:00 |
        Then I get the following call logs in CSV format:
          | Call Date           | Caller            |     Called | Period | user Field |

    Scenario: List call logs in a period
        Given there are only the following call logs:
          | date                | source_name | source_exten | destination_exten | duration | user_field | answered |
          | 2013-01-29 08:46:20 | Père Noël   |         1009 |              1001 |  0:00:03 |            | True     |
          | 2013-01-30 11:20:08 | Bob Marley  |         1002 |        4185550155 |  0:00:03 | Père Noël  | True     |
          | 2013-01-31 11:20:08 | Bob Marley  |         1002 |        4185550155 |  0:00:03 | Père Noël  | True     |
        When I get the list of call logs with arguments:
          | start_date          | end_date            |
          | 2013-01-30T11:11:11 | 2013-01-30T12:12:12 |
        Then I get the following call logs in CSV format:
          | Call Date           | Caller            |     Called | Period | user Field |
          | 2013-01-30T11:20:08 | Bob Marley (1002) | 4185550155 |      3 | Père Noël  |
