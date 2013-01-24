#!/bin/sh
#installation script for package xivo-recording

PF_XIVO_WEB_DEB_FILE="./pf-xivo-web-interface_12.22~20121115.144123.f26d569-2_all.deb"
PY_SETUP="setup.py"
SQL_PATCH="xivo-recording-ddl.sql"

if [ ! -e $PF_XIVO_WEB_DEB_FILE ]; then
    echo "Web interface package (${PF_XIVO_WEB_DEB_FILE}) not found, exiting."
    exit 1
fi

if [ ! -e $PY_SETUP ]; then
    echo "Python setup file (${PY_SETUP}) not found, exiting."
    exit 1
fi

if [ ! -e $SQL_PATCH ]; then
    echo "SQL patch file (${SQL_PATCH}) not found, exiting."
    exit 1
fi

installDep() {
  echo "Installing dependencies..."
  apt-get install -y libevent-dev python-pip python-dev build-essential
  pip install gevent
  pip install tornado
  pip install flask
  pip install SQLAlchemy
  pip install xivo-client-sim
}

installPy() {
  echo "Running python installer..."
  python $PY_SETUP install
}

reloadAsterisk() {
  RECORDING_DIALPLAN="/etc/asterisk/extensions_extra.d/xivo-recording.conf"
  if [ ! -e $RECORDING_DIALPLAN ]; then
      echo "Xivo-recording dialplan configuration file (${RECORDING_DIALPLAN}) not found, exiting."
      exit 1
  fi
  chown asterisk:www-data ${RECORDING_DIALPLAN}
  chmod 660 ${RECORDING_DIALPLAN}
  echo "Reload Asterisk dialplan!"
  asterisk -x 'dialplan reload'
}

installDB() {
  echo "Modifying database..."
  cp $SQL_PATCH /tmp/xivo-recording-ddl.sql
  su - -c 'psql asterisk postgres -f /tmp/xivo-recording-ddl.sql' postgres

  rm /tmp/xivo-recording-ddl.sql
}

installWebI() {
  dpkg -i $PF_XIVO_WEB_DEB_FILE
  if [ $? -ne 0 ]; then
      echo "Installation of new package failed, restoring previous environment..."
      apt-get install pf-xivo-web-interface
      exit 1
  fi	

  echo "Creating web directory..."
  mkdir /var/lib/pf-xivo/sounds/campagnes
}

recordingAutostart() {
  echo "Parameter xivo-recording autostart"
  update-rc.d xivo-recording defaults
}

startRecording() {
  echo "Launching xivo-recording daemon..."
  /etc/init.d/xivo-recording status > /dev/null
  if [ $? -ne 0 ]; then
      /etc/init.d/xivo-recording start
  fi

  /etc/init.d/xivo-recording status
  if [ $? -ne 0 ]; then
      echo "Install failed!"
      exit 1
  else
      echo "Installation finished."
  fi
}

installCron() {
  cp cron_job/delete_old_items /usr/local/bin/delete_old_items
  cp cron_job/log_and_delete /usr/local/bin/log_and_delete
  cp cron_job/xivo-recording.conf /etc/rsyslog.d/xivo-recording.conf
  touch /var/log/asterisk/xivo-recording.log
  /etc/init.d/rsyslog restart
  TMP_CRONTAB=/tmp/crontab
  crontab -l > $TMP_CRONTAB.txt
  echo "0 0 * * *  /usr/local/bin/delete_old_items" >> $TMP_CRONTAB.txt
  crontab $TMP_CRONTAB.txt
  RES=$?
  rm ${TMP_CRONTAB}.txt
  return $RES
}

installAgi() {
  touch /var/log/xivo-recording-agi.log
  chmod o+x /var/log/xivo-recording-agi.log
}

install() {
  installDep
  installPy
  reloadAsterisk
  installDB
  installWebI
  installCron
  installAgi
  recordingAutostart
  startRecording
}


echo "Starting installation..."
echo "Are you sure you want to start XiVO-recording installation?"
echo "(service interruption possible, Asterisk dialplan reload, web interface upodate etc.)"
while true; do
    read -p "(y/n)" yn
    case $yn in
        [Yy]* ) install; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

exit 0


