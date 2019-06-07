FROM python:3.5-stretch
MAINTAINER Wazo Maintainers <dev@wazo.community>

# Configure environment
RUN true && \
    mkdir -p /etc/wazo-confd/conf.d && \
    touch /var/log/wazo-confd.log && \
    chown www-data /var/log/wazo-confd.log && \
    mkdir -p /var/run/wazo-confd /var/lib/asterisk/moh && \
    chown www-data /var/run/wazo-confd /var/lib/asterisk/moh && \
    true

# Add certificates
ADD ./contribs/docker/certs /usr/share/xivo-certs
WORKDIR /usr/share/xivo-certs
RUN openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -nodes -config openssl.cfg -days 3650
RUN chown -R www-data /usr/share/xivo-certs

# Install wazo-confd
ADD . /usr/src/wazo-confd
WORKDIR /usr/src/wazo-confd
RUN true && \
    pip install -r requirements.txt && \
    python setup.py install && \
    cp -av etc/wazo-confd /etc && \
    true

EXPOSE 9486

CMD ["wazo-confd", "-d"]
