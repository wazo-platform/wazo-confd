#!/bin/sh
PYTHONPATH=..:../xivo_recording:../../xivo-tools/client-sim/ lettuce features/recording.feature
