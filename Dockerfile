## Image to build from sources

FROM python:2.7.9
MAINTAINER Wazo Maintainers <dev@wazo.community>

# Install xivo-confd
ADD . /usr/src/xivo-confd
WORKDIR /usr/src/xivo-confd
RUN pip install -r requirements.txt
RUN python setup.py install

# Configure environment
RUN cp -av etc/xivo-confd /etc
RUN mkdir -p /etc/xivo-confd/conf.d

RUN touch /var/log/xivo-confd.log
RUN chown www-data /var/log/xivo-confd.log

RUN mkdir -p /var/run/xivo-confd /var/lib/asterisk/moh
RUN chown www-data /var/run/xivo-confd /var/lib/asterisk/moh

ADD ./contribs/docker/certs /usr/share/xivo-certs
WORKDIR /usr/share/xivo-certs
RUN openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -nodes -config openssl.cfg -days 3650
WORKDIR /usr/src/xivo-confd

EXPOSE 9486

CMD ["xivo-confd", "-fd"]
