Feature: Call logs consultation

    Scenario: List call logs
        Given there are only the following call logs:
          | date                | source_name | source_exten | destination_exten | duration | user_field | answered |
          | 2013-01-30 08:46:20 | Père Noël   |         1009 |              1001 |  0:00:03 |            | True     |
          | 2013-01-30 11:03:47 | Bob Marley  |         1002 |        4185550155 |  0:00:00 |            | False    |
          | 2013-01-30 11:20:08 | Bob Marley  |         1002 |        4185550155 |  0:00:03 | Père Noël  | True     |
        When I get the list of call logs
        Then I get the following call logs in CSV format:
          | Call Date           | Caller            |     Called | Period | user Field |
          | 01/30/2013 08:46:20 | Père Noël (1009)  |       1001 |      3 |            |
          | 01/30/2013 11:03:47 | Bob Marley (1002) | 4185550155 |      0 |            |
          | 01/30/2013 11:20:08 | Bob Marley (1002) | 4185550155 |      3 | Père Noël  |
