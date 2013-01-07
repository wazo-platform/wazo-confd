
Feature: Call recordings management

	In order to create, consult and delete call recordings

	Scenario: Recording creation and consultation
	  Given there is a campaign named "test_campaign"
	  When I save call details for a call referenced by its "callid" in campaign "test_campaign"
	  Then I can consult these details 

	Scenario: Recording search
	  Given there is a campaign of id "1"
	  Given I create a recording for campaign "1" with caller "111" and agent "222"
	  Given I create a recording for campaign "1" with caller "222" and agent "111"
	  Given I create a recording for campaign "1" with caller "123" and agent "123"
	  When I search recordings in the campaign "1" with the key "111"
	  Then I get the first two recordings