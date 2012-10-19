
Feature: Recording campaign management

	In order to execute call quality assessment
	
	Scenario: Campaign creation and consultation
	  When I create a campaign named "blue"
	  Then I can consult this campaign  

	Scenario: Campaign configuration and execution
	  Given there is no campaign "quality",
	  Given I create a campaign named "quality",
	  Given I add queue "5001" for this campaign, 
	  When I start this campaign
	  Then calls placed in this queue are recorded 
	