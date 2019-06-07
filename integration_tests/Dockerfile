FROM wazopbx/wazo-confd

ENV PYTHONDONTWRITEBYTECODE='true'

RUN true && \
    install -dm775 -o www-data -g www-data /var/lib/wazo/sounds/tenants && \
    install -dm777 /usr/share/asterisk/sounds && \
    true

COPY . /usr/src/wazo-confd
WORKDIR /usr/src/wazo-confd
RUN python setup.py develop
