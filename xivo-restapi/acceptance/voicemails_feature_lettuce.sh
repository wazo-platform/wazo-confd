#!/bin/sh
PYTHONPATH=..:../../xivo_restapi:../../../xivo-dao/xivo-dao:../../../xivo-lib-python/xivo-lib-python lettuce features/voicemails.feature --with-xunit --verbosity=3 --xunit-file=xunit-tests-user.xml
