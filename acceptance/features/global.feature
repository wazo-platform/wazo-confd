Feature: WebService up

	In order to check the WebService is working
	
	Scenario: Recording campaign test
	  When I send a "GET" request to "rest/IPBX/recording_campaigns/"
	  Then I get a response with status code "200"
	  
	Scenario: Queues test
	  When I send a "GET" request to "rest/CallCenter/queues/"
	  Then I get a response with status code "200"
	  
	Scenario: Test of whole chain with emulated call
 	  Given there is no campaign
	  Given there is a queue named "test_queue"
	  Given there is an agent "222"
	  Given I create a campaign "test_campaign" pointing to queue "test_queue" with start date "2012-01-01 00:00:00" and end date "2099-05-05 14:59:14"
	  When there was a call from "recording_test" to the queue "test_queue" answered by agent "222"
	  When I read the list of recordings for the campaign "test_campaign" from the database
	  Then I get one and only one item with caller "recording_test", agent "222" and I can read the returned file 
	  