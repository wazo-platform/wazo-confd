FROM python:3.7-slim-buster AS compile-image
LABEL maintainer="Wazo Maintainers <dev@wazo.community>"

RUN python -m venv /opt/venv
# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get -q update
RUN apt-get -yq install gcc

ADD . /usr/src/wazo-confd
WORKDIR /usr/src/wazo-confd
RUN pip install -r requirements.txt
RUN python setup.py install

FROM python:3.7-slim-buster AS build-image
COPY --from=compile-image /opt/venv /opt/venv

COPY ./etc/wazo-confd /etc/wazo-confd
RUN true \
    && mkdir -p /etc/wazo-confd/conf.d \
    && install -o www-data -g www-data /dev/null /var/log/wazo-confd.log \
    && install -d -o www-data -g www-data /run/wazo-confd/ \
    && install -d -o www-data -g www-data /var/lib/asterisk/moh

EXPOSE 9486

# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"
CMD ["wazo-confd", "-d"]
