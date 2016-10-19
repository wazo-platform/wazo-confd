FROM xivo/xivo-confd

COPY . /usr/src/xivo-confd
WORKDIR /usr/src/xivo-confd
RUN python setup.py develop

RUN pip install git+https://github.com/fabianp/memory_profiler.git
