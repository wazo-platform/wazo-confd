Feature: Voicemails management

	Scenario: Voicemails listing
	  Given there is no voicemail
	  Given there is a voicemail with fullname "Test" and with number "123"
	  When I list the voicemails
	  Then I get a response from voicemails webservice with status "200"
	  Then I get one voicemail with fullname "Test" and with number "123"

	Scenario: Voicemails edition
	  Given there is no voicemail
	  Given there is a voicemail with fullname "Test" and with number "123"
	  When I update the voicemail of number "123" with number "456" and fullname "New Test"
	  Then I get a response from voicemails webservice with status "200"
	  Then there is a voicemail with number "456" and fullname "New Test"
	  
	Scenario: Editing a non existing voicemail
	  Given there is no voicemail
	  When I update the voicemail of id "1"
	  Then I get a response from voicemails webservice with status "404"
	  
	Scenario: Editing a voicemail with invalid data
	  Given there is no voicemail
	  Given there is a voicemail with fullname "Test" and with number "123"
	  When I update the voicemail of number "123" with a field "unexisting_field" of value "value"
	  Then I get a response from voicemails webservice with status "400"
	  Then I get an error message from voicemails webservice "Incorrect parameters sent: unexisting_field"