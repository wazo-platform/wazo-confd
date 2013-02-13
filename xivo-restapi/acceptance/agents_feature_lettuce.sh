#!/bin/sh
PYTHONPATH=..:../../xivo_restapi:../../../xivo-dao/xivo-dao lettuce features/agents.feature --with-xunit --verbosity=3 --xunit-file=xunit-tests-agent.xml
