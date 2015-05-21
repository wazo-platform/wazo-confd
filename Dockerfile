## Image to build from sources

FROM debian:latest
MAINTAINER XiVO Team "dev@avencall.com"

ENV DEBIAN_FRONTEND noninteractive
ENV HOME /root

# Add dependencies
RUN apt-get -qq update
RUN apt-get -qq -y install \
    wget \
    apt-utils \
    python-pip \
    git \
    libpq-dev \
    python-dev \
    libyaml-dev

# Install xivo-amid
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

WORKDIR /root

# Clean
RUN apt-get clean

EXPOSE 9486

CMD xivo-confd -f -d
