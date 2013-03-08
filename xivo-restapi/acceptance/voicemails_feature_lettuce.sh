#!/bin/sh
PYTHONPATH=..:../../xivo_restapi:../../../xivo-dao/xivo-dao lettuce features/voicemails.feature --with-xunit --verbosity=3 --xunit-file=xunit-tests-agent.xml
