FROM python:3.7-buster
MAINTAINER Wazo Maintainers <dev@wazo.community>

# Configure environment
RUN true && \
    mkdir -p /etc/wazo-confd/conf.d && \
    touch /var/log/wazo-confd.log && \
    chown www-data /var/log/wazo-confd.log && \
    mkdir -p /run/wazo-confd /var/lib/asterisk/moh && \
    chown www-data /run/wazo-confd /var/lib/asterisk/moh && \
    true

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
