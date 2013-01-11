Feature: Call recordings management

	In order to create, consult and delete call recordings

	Scenario: Recording creation exception
	  Given there is a campaign named "test_campaign"
	  Given there is no agent with number "1111"
	  When I save call details for a call referenced by its "callid" in campaign "test_campaign" replied by agent with number "1111"
	  Then I get a response with error code '400' and message 'SQL Error: No such agent'

	Scenario: Recording creation and consultation
	  Given there is a campaign named "test_campaign"
	  Given there is an agent with number "1111"
	  When I save call details for a call referenced by its "callid" in campaign "test_campaign" replied by agent with number "1111"
	  Then I can consult these details
	  Then I delete this recording and the agent "1111"

	Scenario: Recording consultation and removing
	  Given there is a campaign named "test_campaing"
	  Given there is an agent of number "222"
	  Given there is a recording referenced by a "callid" with agent "222"
	  When I delete a recording referenced by this "callid"
	  Then the recording is deleted and I get a response with code "200"


	Scenario: Deleting of unexisting recording
	  Given there is a campaign named "test_campaign"
	  Given there is no recording referenced by a "callid" in campaign "test_campaign"
	  When I delete a recording referenced by this "callid"
	  Then I get a response with error code '404' with message 'No such recording'
	  

	Scenario: Recording search
	  Given there is a campaign of id "1"
	  Given there is an agent "222"
	  Given there is an agent "111"
	  Given there is an agent "123"
	  Given I create a recording for campaign "1" with caller "111" and agent "222"
	  Given I create a recording for campaign "1" with caller "222" and agent "111"
	  Given I create a recording for campaign "1" with caller "123" and agent "123"
	  When I search recordings in the campaign "1" with the key "111"
	  Then I get the first two recordings
	  