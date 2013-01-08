
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

	  
	Scenario: Recording consultation and removing
	  Given there is a campaign named "test_campaing"
	  Given there is a recording referenced by a "callid"
	  When I delete a recording referenced by this "callid"
	  Then the recording is deleted and I get a response with code "200"

	Scenario: Deleting of unexisting recording
	  Given there is a campaign named "test_campaing"
	  Given there is no recording referenced by a "callid"
	  When I delete a recording referenced by this "callid"
	  Then I get a response with error code '400' with message 'No such recording'
	  