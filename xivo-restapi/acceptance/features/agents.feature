Feature: In order to get agents' details

	Scenario: Agents listing
	  Given there is an agent named "Tomá š" with number "2006"
	  Given there is an agent named "John" with number "2005"
	  Given there is an agent named "autre" with number "2007"
	  When I ask for all agents
	  Then there is an agent named "John" with number "2005" in the response
	  Then there is an agent named "Tomá š" with number "2006" in the response
	  Then there is an agent named "autre" with number "2007" in the response