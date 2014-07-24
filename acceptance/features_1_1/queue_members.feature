Feature: REST API Manipulate queue members

    Scenario: Get agent-queue association
        Given there is a agent "John" "2404" with extension "2404@default"
        Given there are queues with infos:
            | name       | display name | number | context | agents_number |
            | superqueue | SuperQueue   | 3007   | default | 2404          |
        Given the agent "2404" has the penalty "5" for the queue "superqueue"
        When I request the queue member information for the queue "superqueue" and the agent "2404"
        Then I get a response with status "200"
        Then I get a queue membership with the following parameters:
            | penalty |
            | 5       |

    Scenario: Get agent-queue association on non-existing queue
        Given there is no queue with id "4876"
        When I request the queue member information for the queue with id "4876" and the agent with id "5200"
        Then I get a response with status "404"
        Then I get an error message "Queue with id=4876 does not exist"

    Scenario: Get agent-queue association on non-associated agent
        Given there is a agent "John" "2404" with extension "2404@default"
        Given there are queues with infos:
            | name       | display name | number | context |
            | superqueue | SuperQueue   | 3007   | default |
        When I request the queue member information for the queue "superqueue" and the agent "2404"
        Then I get a response with status "404"
        Then I get an error message matching "QueueMember with agent_id=\d+ queue_id=\d+ does not exist"

    Scenario: Editing an agent-queue association
        Given there is a agent "John" "2404" with extension "2404@default"
        Given there are queues with infos:
            | name       | display name | number | context | agents_number |
            | superqueue | SuperQueue   | 3007   | default | 2404          |
        Given the agent "2404" has the penalty "5" for the queue "superqueue"
        When I edit the member information for the queue "superqueue" and the agent "2404" with the penalty "7"
        Then I get a response with status "204"
        Then the penalty is "7" for queue "superqueue" and agent "2404"

    Scenario: Editing agent-queue association on non-existing queue
        Given there is no queue with id "4876"
        When I edit the member information for the queue with id "4876" and the agent with id "5200" with the penalty "7"
        Then I get a response with status "404"
        Then I get an error message matching "Queue with id=\d+ does not exist"

    Scenario: Editing agent-queue association on non-associated agent
        Given there is a agent "John" "2404" with extension "2404@default"
        Given there are queues with infos:
            | name       | display name | number | context |
            | superqueue | SuperQueue   | 3007   | default |
        When I edit the member information for the queue "superqueue" and the agent "2404" with the penalty "7"
        Then I get a response with status "404"
        Then I get an error message matching "QueueMember with agent_id=\d+ queue_id=\d+ does not exist"

