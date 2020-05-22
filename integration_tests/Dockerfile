FROM wazopbx/wazo-confd

ENV PYTHONDONTWRITEBYTECODE='true'

COPY . /usr/src/wazo-confd
WORKDIR /usr/src/wazo-confd
RUN python setup.py develop
