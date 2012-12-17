
Feature: Recording campaign management

	In order to execute call quality assessment
	
	Scenario: Campaign creation and consultation
	  When I create a campaign named "test_campaign"
	  Then I can consult this campaign  
	  
	Scenario: Get activated campaigns
	  Given there is an activated campaign named "quality" focusing queue "prijem"
	  Given there is an non activated campaign named "disabled" focusing queue "accueil"	   
	  When I ask for activated campaigns for queue "prijem"
	  Then I get a list of activated campaigns with campaign "prijem"

	Scenario: Campaign configuration and execution
	  Given there is no campaign "quality",
	  Given I create a campaign named "quality",
	  Given I add queue "5001" for this campaign, 
	  When I start this campaign
	  Then calls placed in this queue are recorded 
	