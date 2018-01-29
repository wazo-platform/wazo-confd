FROM wazopbx/xivo-confd

RUN true && \
    mkdir -p /var/lib/xivo/sounds && \
    mkdir -p /var/lib/xivo/sounds/acd && \
    mkdir -p /var/lib/xivo/sounds/features && \
    mkdir -p /var/lib/xivo/sounds/playback && \
    mkdir -p /var/lib/xivo/sounds/recordings && \
    mkdir -p /var/lib/xivo/sounds/monitor && \
    mkdir -p /var/lib/xivo/sounds/recordings-meetme && \
    chmod -R 777 /var/lib/xivo/sounds && \
    mkdir -p /usr/share/asterisk/sounds && \
    chmod -R 777 /usr/share/asterisk/sounds

COPY . /usr/src/xivo-confd
WORKDIR /usr/src/xivo-confd
RUN python setup.py develop
