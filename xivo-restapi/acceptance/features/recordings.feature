Feature: Call recordings management

	In order to create, consult and delete call recordings

	Scenario: Recording creation exception
	  Given there is no campaign
	  Given there is a queue named "test_queue"
	  Given there is a campaign named "test_campaign" for a queue "test_queue"
	  Given there is no agent with number "1111"
	  When I save call details with the following parameters:
	  	| callid | campaign_name | agent_no | caller |
	  	|  abcd  | test_campaign |   1111   |        |
	  Then I get a response with error code '400' and message 'SQL Error: No such agent'

	Scenario: Recording creation and consultation
	  Given there is no campaign
	  Given there is a queue named "test_queue"
	  Given there is a campaign named "test_campaign" for a queue "test_queue"
	  Given there is an agent with number "1111"
	  When I save call details with the following parameters:
	  	| callid | campaign_name | agent_no | caller |
	  	|  abcd  | test_campaign |   1111   |        |
	  Then I can consult the recording "abcd" in campaign "test_campaign"

	Scenario: Recording consultation and removing
	  Given there is no campaign
	  Given there is a queue named "test_queue"
	  Given there is a campaign named "test_campaign" for a queue "test_queue"
	  Given there is an agent of number "222"
	  Given there are recordings with the following values:
	  	| callid | campaign_name | agent_no | caller |
	  	|  abcd  | test_campaign |    222   |        |
	  When I delete a recording referenced by this "abcd" in campaign "test_campaign"
	  Then the recording is deleted and I get a response with code "200"

	Scenario: Deleting of unexisting recording
	  Given there is no campaign
	  Given there is a queue named "test_queue"
	  Given there is a campaign named "test_campaign" for a queue "test_queue"
	  Given there is no recording referenced by a "callid" in campaign "test_campaign"
	  When I delete a recording referenced by this "callid" in campaign "test_campaign"
	  Then I get a response with error code '404' with message 'No such recording'
	  

	Scenario: Recording search
	  Given there is no campaign
	  Given there is a campaign "campaign1"
	  Given there is an agent "222"
	  Given there is an agent "111"
	  Given there is an agent "123"
	  Given there are recordings with the following values:
	  	| callid | campaign_name | agent_no | caller |
	  	|  abcd  |   campaign1   |    222   |   111  |
	  	|  efgh  |   campaign1   |    111   |   222  |
	  	|  ijkl  |   campaign1   |    123   |   123  |
	  When I search recordings in the campaign "campaign1" with the key "111"
	  Then I get the first two recordings
	  
	Scenario: Consistent number of recordings
	  Given there is no campaign
	  Given there is a campaign "campaign1"
	  Given there is an agent "222"
	  Given there are at least "10" recordings for campaign "campaign1" and agent "222"
	  When I ask for the recordings of "campaign1"
	  Then the displayed total is equal to the actual number of recordings
	  
	Scenario: Recording pagination
	  Given there is no campaign
	  Given there is a campaign "campaign1"
	  Given there is an agent "222"
	  Given there are at least "10" recordings for campaign "campaign1" and agent "222"
	  When I ask for a list of recordings for "campaign1" with page "1" and page size "5"
	  Then I get exactly "5" recordings
	  
	Scenario: No overlapping when paginating recordings
	  Given there is no campaign
	  Given there is a campaign "campaign1"
	  Given there is an agent "222"
	  Given there are at least "10" recordings for campaign "campaign1" and agent "222"
	  Given I ask for a list of recordings for "1" with page "1" and page size "5"
	  Given I ask for a list of recordings for "1" with page "2" and page size "5"
	  Then the two lists of recording do not overlap
	
	Scenario: Pagination of search result
	  Given there is no campaign
	  Given there is a campaign "campaign1"
	  Given there is an agent "222"
	  Given there are at least "10" recordings for campaign "campaign1" and agent "222"
	  When we search recordings in the campaign "campaign1" with the key "222", page "2" and page size "5"
	  Then I get exactly "5" recordings
