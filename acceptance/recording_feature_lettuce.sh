#!/bin/sh
PYTHONPATH=..:../xivo_recording:../../xivo-dao/xivo-dao lettuce features/recordings.feature
