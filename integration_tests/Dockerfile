FROM wazopbx/xivo-confd

RUN true && \
    mkdir -p /var/lib/xivo/sounds/acd && \
    mkdir -p /var/lib/xivo/sounds/features && \
    mkdir -p /var/lib/xivo/sounds/playback && \
    mkdir -p /var/lib/xivo/sounds/recordings && \
    mkdir -p /var/lib/xivo/sounds/monitor && \
    mkdir -p /var/lib/xivo/sounds/recordings-meetme && \
    chmod -R 777 /var/lib/xivo/sounds

RUN true && \
    mkdir -p /var/lib/xivo/sounds/hard-coded/fr_FR && \
    touch /var/lib/xivo/sounds/hard-coded/fr_FR/ivr.mp3 && \
    chmod 777 /var/lib/xivo/sounds/hard-coded && \
    chmod 555 /var/lib/xivo/sounds/hard-coded/fr_FR && \
    chmod 444 /var/lib/xivo/sounds/hard-coded/fr_FR/ivr.mp3

RUN true && \
    mkdir -p /usr/share/asterisk/sounds/fr_FR && \
    mkdir -p /usr/share/asterisk/sounds/fr_CA && \
    echo -n "asterisk_sound_ogg_fr_FR" > /usr/share/asterisk/sounds/fr_FR/conf-now-unmuted.ogg && \
    echo -n "asterisk_sound_slin_fr_FR" > /usr/share/asterisk/sounds/fr_FR/conf-now-unmuted.wav && \
    echo -n "asterisk_sound_ogg_fr_CA" > /usr/share/asterisk/sounds/fr_CA/conf-now-unmuted.ogg && \
    chmod -R 777 /usr/share/asterisk/sounds

COPY . /usr/src/xivo-confd
WORKDIR /usr/src/xivo-confd
RUN python setup.py develop
