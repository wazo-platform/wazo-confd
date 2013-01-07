
Feature: Call recordings management

	In order to create, consult and delete call recordings

	Scenario: Recording creation and consultation
	  Given there is a campaign named "test_campaign"
	  Given there is an agent with number "1111"
	  When I save call details for a call referenced by its "callid" in campaign "test_campaign" replied by agent with number "1111"
	  Then I can consult these details 
