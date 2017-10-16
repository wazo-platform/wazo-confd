## Image to build from sources

FROM python:2.7.13-alpine
MAINTAINER Wazo Maintainers <dev@wazo.community>


# Install xivo-confd
ADD . /usr/src/xivo-confd
WORKDIR /usr/src/xivo-confd
RUN apk add --no-cache git postgresql-dev
RUN apk add --no-cache musl-dev linux-headers gcc \
    && pip install -r requirements.txt \
    && apk del -r --purge musl-dev linux-headers gcc
RUN python setup.py install

# Configure environment
RUN cp -av etc/xivo-confd /etc
RUN mkdir -p /etc/xivo-confd/conf.d

RUN touch /var/log/xivo-confd.log
RUN adduser -HD www-data
RUN chown www-data /var/log/xivo-confd.log

RUN mkdir -p /var/run/xivo-confd /var/lib/asterisk/moh
RUN chown www-data /var/run/xivo-confd /var/lib/asterisk/moh

ADD ./contribs/docker/certs /usr/share/xivo-certs
WORKDIR /usr/share/xivo-certs
RUN apk add --no-cache openssl \
    && openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -nodes -config openssl.cfg -days 3650 \
    && apk del -r --purge openssl
WORKDIR /usr/src/xivo-confd

EXPOSE 9486

CMD ["xivo-confd", "-fd"]
