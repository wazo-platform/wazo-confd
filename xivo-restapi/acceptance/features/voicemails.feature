Feature: Voicemails management

	Scenario: Voicemails listing
	  Given there is no voicemail
	  Given there is a voicemail with fullname "Test" and with number "123"
	  When I list the voicemails
	  Then I get a response from voicemails webservice with status "200"
	  Then I get one voicemail with fullname "Test" and with number "123"
