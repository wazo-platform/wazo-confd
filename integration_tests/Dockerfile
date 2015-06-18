FROM xivo/xivo-confd

ADD integration_tests/mock_sysconfd /usr/src/mock_sysconfd

ADD . /usr/src/xivo-confd
WORKDIR /usr/src/xivo-confd
RUN python setup.py install

