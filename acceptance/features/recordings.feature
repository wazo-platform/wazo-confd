
Feature: Call recordings management

	In order to create, consult and delete call recordings

	Scenario: Recording creation and consultation
	  Given there is a campaign named "test_campaign"
	  When I save call details for a call referenced by its "callid" in campaign "test_campaign"
	  Then I can consult these details 
