FROM wazopbx/xivo-confd

RUN mkdir -p /var/lib/xivo/sounds

RUN mkdir -p /var/lib/xivo/sounds/acd
RUN mkdir -p /var/lib/xivo/sounds/features
RUN mkdir -p /var/lib/xivo/sounds/playback
RUN mkdir -p /var/lib/xivo/sounds/recordings

RUN mkdir -p /var/lib/xivo/sounds/monitor
RUN mkdir -p /var/lib/xivo/sounds/recordings-meetme

RUN chmod -R 777 /var/lib/xivo/sounds

COPY . /usr/src/xivo-confd
WORKDIR /usr/src/xivo-confd
RUN python setup.py develop
