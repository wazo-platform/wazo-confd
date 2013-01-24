#!/bin/sh
PYTHONPATH=..:../xivo_recording:../../xivo-dao/xivo-dao lettuce features/recordings.feature --with-xunit --verbosity=3 --xunit-file=xunit-tests-recording.xml
