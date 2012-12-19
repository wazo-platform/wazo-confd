#!/bin/sh
PYTHONPATH=..:../xivo_recording:../../xivo-dao lettuce features/queues.feature
