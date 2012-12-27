Feature: Recording campaign management

	In order to execute call quality assessment
	
	Scenario: Campaign creation and consultation
	  When I create a campaign "test_campaign"
	  Then I can consult this campaign  
	  
	Scenario: Get activated campaigns
	  Given there is an activated campaign named "quality" focusing queue "1"
	  Given there is an non activated campaign named "disabled" focusing queue "2"	   
	  When I ask for activated campaigns for queue "1"
	  Then I get a list of activated campaigns with campaign "quality"

	Scenario: Campaign configuration and execution
	  Given there is no campaign "quality",
	  Given I create a campaign named "quality",
	  Given I add queue "5001" for this campaign, 
	  When I start this campaign
	  Then calls placed in this queue are recorded 
	
	Scenario: Campaign edition
	  Given there is a queue "1" and a queue "2"
	  Given I create a campaign "lettuce" pointing to queue "1"
	  When I change its name to "lettuce_updated" and its queue to "2"
	  Then its name and queue are actually modified

	Scenario: Consulting running and activated campaigns for a given queue
	  Given there is a queue "1" and a queue "2"
	  Given I create an activated campaign "lettuce1" pointing to queue "1" currently running
	  Given I create an activated campaign "lettuce2" pointing to queue "2" currently running
	  Given I create a non activated campaign "lettuce3" pointing to queue "1" currently running
	  Given I create an activated campaign "lettuce4" pointing to queue "1" currently not running
	  When I ask for running and activated campaigns for queue "1"
	  Then I get campaign "lettuce1", I do not get "lettuce2", "lettuce3", "lettuce4"