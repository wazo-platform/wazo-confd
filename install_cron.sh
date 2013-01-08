#!/bin/sh
cp delete_old_items /usr/local/bin/delete_old_items
chmod u+x /usr/local/bin/delete_old_items
TMP_CRONTAB=/tmp/crontab
crontab -l > $TMP_CRONTAB.txt
echo "0 0 * * *  /usr/local/bin/delete_old_items" >> $TMP_CRONTAB.txt
crontab $TMP_CRONTAB.txt
RES=$?
rm ${TMP_CRONTAB}.txt
return $RES
