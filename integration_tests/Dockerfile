FROM wazoplatform/wazo-confd

ENV PYTHONDONTWRITEBYTECODE='true'

COPY . /usr/src/wazo-confd
WORKDIR /usr/src/wazo-confd
RUN python3 -m pip install -e .
