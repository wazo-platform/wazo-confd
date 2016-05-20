## Image to build from sources

FROM python:2.7.9
MAINTAINER XiVO Team "dev@avencall.com"

# Install xivo-confd
ADD . /usr/src/xivo-confd
WORKDIR /usr/src/xivo-confd
RUN pip install -r requirements.txt
RUN python setup.py install

# Configure environment
RUN touch /var/log/xivo-confd.log
RUN mkdir /etc/xivo-confd/
RUN cp /usr/src/xivo-confd/etc/xivo-confd/*.yml /etc/xivo-confd/
RUN mkdir /etc/xivo-confd/conf.d
RUN mkdir /var/run/xivo-confd
RUN chown www-data /var/run/xivo-confd

EXPOSE 9486

CMD ["xivo-confd", "-fd"]
