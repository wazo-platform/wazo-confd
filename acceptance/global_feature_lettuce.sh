#!/bin/sh
PYTHONPATH=..:../xivo_recording:../../xivo-dao/xivo-dao lettuce features/global.feature --with-xunit --verbosity=3 --xunit-file=xunit-tests-recording.xml
