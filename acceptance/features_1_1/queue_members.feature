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
        Then I get an error message matching "Resource Not Found - Queue was not found"

    Scenario: Get agent-queue association on non-existing agent
        Given there are queues with infos:
            | name       | display name | number | context |
            | superqueue | SuperQueue   | 3007   | default |
        Given there is no agent with id "4856"
        When I request the following queue member:
            | queue_name | agent_id |
            | superqueue | 4856     |
        Then I get a response with status "404"
        Then I get an error message matching "Resource Not Found - Agent was not found"

    Scenario: Get agent-queue association on non-associated agent
        Given there is a agent "John" "2404" with extension "2404@default"
        Given there are queues with infos:
            | name       | display name | number | context |
            | superqueue | SuperQueue   | 3007   | default |
        When I request the following queue member:
            | queue_name | agent_number |
            | superqueue | 2404         |
        Then I get a response with status "404"
        Then I get an error message matching "Resource Not Found - QueueMember was not found"

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
        Then I get an error message matching "Resource Not Found - Queue was not found"

    Scenario: Editing agent-queue association on non-existing agent
        Given there are queues with infos:
            | name       | display name | number | context |
            | superqueue | SuperQueue   | 3007   | default |
        Given there is no agent with id "4856"
        When I edit the following queue member:
            | queue_name | agent_id | penalty |
            | superqueue | 4856     | 7       |
        Then I get a response with status "404"
        Then I get an error message matching "Resource Not Found - Agent was not found"

    Scenario: Editing agent-queue association on non-associated agent
        Given there is a agent "John" "2404" with extension "2404@default"
        Given there are queues with infos:
            | name       | display name | number | context |
            | superqueue | SuperQueue   | 3007   | default |
        When I edit the following queue member:
            | queue_name | agent_number | penalty |
            | superqueue | 2404         | 7       |
        Then I get a response with status "404"
        Then I get an error message matching "Resource Not Found - QueueMember was not found"

    Scenario: Associate an agent to a queue
        Given there is a agent "Bob" "2407" with extension "2407@default"
        Given there are queues with infos:
            | name       | display name | number | context |
            | bluesky    | BlueSky      | 3012   | default |
        When I associate the following agent:
            | queue_name | agent_number | penalty |
            | bluesky    | 2407         | 5       |
        Then I get a response with status "201"
        Then the penalty is "5" for queue "bluesky" and agent "2407"

    Scenario: Associate an agent to a non-existing queue
        Given there is a agent "Boy" "2406" with extension "2406@default"
        Given there is no queue with id "4877"
        When I associate the following agent:
            | queue_id | agent_number | penalty |
            | 4877     | 2406     | 4       |
        Then I get a response with status "404"
        Then I get an error message matching "Resource Not Found - Queue was not found"

    Scenario: Associate an non existing agent to a queue
        Given there is no agent with id "4859"
        Given there are queues with infos:
            | name       | display name | number | context |
            | bluesky    | BlueSky      | 3012   | default |
        When I associate the following agent:
            | queue_name | agent_id     | penalty |
            | bluesky    | 4859         | 5       |
        Then I get a response with status "400"
        Then I get an error message matching "Input Error - field 'agent_id': Agent was not found"

    Scenario: Associate an agent to a queue already associated
        Given there is a agent "Bob" "2407" with extension "2407@default"
        Given there are queues with infos:
            | name       | display name | number | context | agents_number |
            | bluesky    | BlueSky      | 3012   | default | 2407          |
        When I associate the following agent:
            | queue_name | agent_number | penalty |
            | bluesky    | 2407         | 5       |
        Then I get a response with status "400"
        Then I get an error message matching "Resource Error - Agent is associated with a Queue"
