Feature: In order to get some information on queues

	Scenario: Queues listing
	  When I create a queue "my_queue"
	  Then I can consult the queue "my_queue" and the other ones