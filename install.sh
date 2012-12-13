#!/bin/sh
#installation script for package xivo-recording

PF_XIVO_WEB_DEB_FILE="pf-xivo-web-interface_12.21~20121212.134631.6cf6e1f-3_all.deb"

echo "Starting installation..."

echo "Installing dependencies..."
apt-get install -y libevent-dev python-pip python-dev build-essential
pip install gevent
pip install flask
pip install SQLAlchemy
pip install xivo-client-sim

echo "Running python installer..."
python setup.py install

echo "Modifying database..."
cp xivo-recording-ddl.sql /tmp/xivo-recording-ddl.sql
su - -c 'psql asterisk postgres -f /tmp/xivo-recording-ddl.sql' postgres

rm /tmp/xivo-recording-ddl.sql

dpkg -i $PF_XIVO_WEB_DEB_FILE
if [ $? -ne 0 ]; then
    echo "Installation of new package failed, restoring previous environment..."
    apt-get install pf-xivo-web-interface
    exit 1
fi	

update-rc.d xivo-recording defaults

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


exit 0


