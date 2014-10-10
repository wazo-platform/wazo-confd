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
    ssh \
    libpq-dev \
    python-dev \
    libyaml-dev \
    nginx \
    net-tools

# Install xivo-amid
WORKDIR /root
RUN git clone "git://github.com/xivo-pbx/xivo-confd"
WORKDIR xivo-confd
RUN pip install -r requirements.txt
RUN python setup.py install

# Configure environment
RUN touch /var/log/xivo-confd.log
RUN cp debian/xivo-confd.init /etc/init.d/xivo-confd
RUN mkdir -p /etc/xivo/xivo-confd
RUN mkdir /var/run/xivo-confd
RUN mkdir /var/www
RUN chown www-data: /var/log/xivo-confd.log
RUN chown www-data: /var/www
RUN chown www-data: /var/run/xivo-confd

# Configure nginx
RUN cp etc/nginx/sites-available/xivo-confd /etc/nginx/sites-available/xivo-confd
RUN ln -s /etc/nginx/sites-available/xivo-confd /etc/nginx/sites-enabled/xivo-confd

# Add script to run services
ADD xivo-confd-service /root/xivo-confd-service
RUN chmod +x /root/xivo-confd-service

# Set password
RUN echo "root:xivo" | chpasswd

# Clean
RUN apt-get clean

EXPOSE 9486

CMD /root/xivo-confd-service
