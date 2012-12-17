#!/bin/sh
PYTHONPATH=..:../xivo_recording:../../xivo-dao/xivo-dao/xivo_dao lettuce features/campaigns.feature
PYTHONPATH=..:../xivo_recording:../../xivo-dao/xivo-dao/xivo_dao lettuce features/recordings.feature
