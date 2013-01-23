#!/bin/sh
PYTHONPATH=..:../xivo_recording:../../xivo-dao/xivo-dao lettuce features/queues.feature --with-xunit --verbosity=3 --xunit-file=xunit-tests-queue.xml
