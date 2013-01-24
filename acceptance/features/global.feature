Feature: WebService up

	In order to check the WebService is working
	
	Scenario: Recording campaign test
	  When I send a "GET" request to "rest/IPBX/recording_campaigns/"
	  Then I get a response with status code "200"
	  
	Scenario: Queues test
	  When I send a "GET" request to "rest/CallCenter/queues/"
	  Then I get a response with status code "200"