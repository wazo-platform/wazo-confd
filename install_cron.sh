#!/bin/sh
test -x /etc/cron.minutely || mkdir /etc/cron.minutely
cp delete_old_items /etc/cron.minutely/delete_old_items
chmod u+x /etc/cron.minutely/delete_old_items
TMP_CRONTAB=/tmp/crontab
crontab -l > $TMP_CRONTAB.txt
echo "* * * * *  cd / && run-parts --report /etc/cron.minutely" >> $TMP_CRONTAB.txt
crontab $TMP_CRONTAB.txt
RES=$?
rm ${TMP_CRONTAB}.txt
return $RES
