#
# cron jobs for wazo-confd
#

24 3 * * * root /usr/bin/wazo-confd-purge-meetings --quiet
42 3 * * * root /usr/bin/wazo-confd-sync-db --quiet
