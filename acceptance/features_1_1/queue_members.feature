Feature: REST API Manipulate queue members

    Scenario: Get agent-queue association
        Given there is a agent "John" "2404" with extension "2404@default"
        Given there are queues with infos:
            | name       | display name | number | context | agents_number |
            | superqueue | SuperQueue   | 3007   | default | 2404          |
        Given the agent "2404" has the penalty "5" for the queue "superqueue"
        When I request the following queue member:
            | queue_name | agent_number |
            | superqueue | 2404         |
        Then I get a response with status "200"
        Then I get a queue membership with the following parameters:
            | penalty |
            | 5       |

    Scenario: Get agent-queue association on non-existing queue
        Given there is no queue with id "4876"
        When I request the following queue member:
            | queue_id | agent_id |
            | 4876     | 5200     |
        Then I get a response with status "404"
        Then I get an error message "Queue with id=4876 does not exist"

    Scenario: Get agent-queue association on non-existing agent
        Given there are queues with infos:
            | name       | display name | number | context |
            | superqueue | SuperQueue   | 3007   | default |
        Given there is no agent with id "4856"
        When I request the following queue member:
            | queue_name | agent_id |
            | superqueue | 4856     |
        Then I get a response with status "404"
        Then I get an error message "Agent with id=4856 does not exist"

    Scenario: Get agent-queue association on non-associated agent
        Given there is a agent "John" "2404" with extension "2404@default"
        Given there are queues with infos:
            | name       | display name | number | context |
            | superqueue | SuperQueue   | 3007   | default |
        When I request the following queue member:
            | queue_name | agent_id |
            | superqueue | 4856     |
        Then I get a response with status "404"
        Then I get an error message matching "QueueMember with agent_id=\d+ queue_id=\d+ does not exist"

    Scenario: Editing an agent-queue association
        Given there is a agent "John" "2404" with extension "2404@default"
        Given there are queues with infos:
            | name       | display name | number | context | agents_number |
            | superqueue | SuperQueue   | 3007   | default | 2404          |
        Given the agent "2404" has the penalty "5" for the queue "superqueue"
        When I edit the following queue member:
            | queue_name | agent_number | penalty |
            | superqueue | 2404         | 7       |
        Then I get a response with status "204"
        Then the penalty is "7" for queue "superqueue" and agent "2404"

    Scenario: Editing agent-queue association on non-existing queue
        Given there is no queue with id "4876"
        When I edit the following queue member:
            | queue_id | agent_id | penalty |
            | 4876     | 5200     | 7       |
        Then I get a response with status "404"
        Then I get an error message matching "Queue with id=\d+ does not exist"

    Scenario: Editing agent-queue association on non-existing agent
        Given there are queues with infos:
            | name       | display name | number | context |
            | superqueue | SuperQueue   | 3007   | default |
        Given there is no agent with id "4856"
        When I edit the following queue member:
            | queue_name | agent_id | penalty |
            | superqueue | 4856     | 7       |
        Then I get a response with status "404"
        Then I get an error message "Agent with id=4856 does not exist"

    Scenario: Editing agent-queue association on non-associated agent
        Given there is a agent "John" "2404" with extension "2404@default"
        Given there are queues with infos:
            | name       | display name | number | context |
            | superqueue | SuperQueue   | 3007   | default |
        When I edit the following queue member:
            | queue_name | agent_number | penalty |
            | superqueue | 2404         | 7       |
        Then I get a response with status "404"
        Then I get an error message matching "QueueMember with agent_id=\d+ queue_id=\d+ does not exist"
