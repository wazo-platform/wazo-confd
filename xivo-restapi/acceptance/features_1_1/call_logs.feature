Feature: Call logs consultation

    Scenario: List call logs
        Given there are only the following call logs between "2013-01-01" and "2013-01-02":
          | date                | source_name | source_exten | destination_exten | duration | user_field | answered |
          | 2013-01-01 08:46:20 | Père Noël   |         1009 |              1001 |  0:00:03 |            | True     |
          | 2013-01-01 11:03:47 | Bob Marley  |         1002 |        4185550155 |  0:00:00 |            | False    |
          | 2013-01-01 11:20:08 | Bob Marley  |         1002 |        4185550155 |  0:00:03 | Père Noël  | True     |
        When I get the list of call logs
        Then I get the following call logs in CSV format:
          | Call Date           | Caller            |     Called | Period | user Field |
          | 2013-01-01 08:46:20 | Père Noël (1009)  |       1001 |      3 |            |
          | 2013-01-01 11:03:47 | Bob Marley (1002) | 4185550155 |      0 |            |
          | 2013-01-01 11:20:08 | Bob Marley (1002) | 4185550155 |      3 | Père Noël  |
