## Image to build from sources

FROM python:2.7.13
MAINTAINER Wazo Maintainers <dev@wazo.community>

# Configure environment
RUN true && \
    mkdir -p /etc/xivo-confd/conf.d && \
    touch /var/log/xivo-confd.log && \
    chown www-data /var/log/xivo-confd.log && \
    mkdir -p /var/run/xivo-confd /var/lib/asterisk/moh && \
    chown www-data /var/run/xivo-confd /var/lib/asterisk/moh && \
    true

# Add certificates
ADD ./contribs/docker/certs /usr/share/xivo-certs
WORKDIR /usr/share/xivo-certs
RUN openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -nodes -config openssl.cfg -days 3650

# Install xivo-confd
ADD . /usr/src/xivo-confd
WORKDIR /usr/src/xivo-confd
RUN true && \
    pip install -r requirements.txt && \
    python setup.py install && \
    cp -av etc/xivo-confd /etc && \
    true

EXPOSE 9486

CMD ["xivo-confd", "-d"]
