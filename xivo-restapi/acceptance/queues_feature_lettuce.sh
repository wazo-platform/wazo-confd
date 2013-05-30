#!/bin/sh
PYTHONPATH=..:../../xivo_restapi:../../../xivo-dao/xivo-dao:../../../xivo-lib-python/xivo-lib-python:../../../xivo-acceptance lettuce features/queues.feature --with-xunit --verbosity=3 --xunit-file=xunit-tests-queue.xml
