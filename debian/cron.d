#
# cron jobs for wazo-confd
#

42 3 * * * root /usr/bin/wazo-confd-sync-db --quiet
