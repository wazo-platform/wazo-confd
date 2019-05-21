FROM wazopbx/xivo-confd

RUN true && \
    install -dm775 -o www-data -g www-data /var/lib/wazo/sounds/tenants && \
    install -dm777 /usr/share/asterisk/sounds && \
    true

COPY . /usr/src/xivo-confd
WORKDIR /usr/src/xivo-confd
RUN python setup.py develop
