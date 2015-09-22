.PHONY: test-image test-setup distclean

PROVD_DIR=../../xivo-provisioning
MANAGE_DB_DIR=../../xivo-manage-db/
POSTGRES_DOCKER=$(MANAGE_DB_DIR)/contribs/xivo-postgres/Dockerfile


test-setup: build-postgres build-provd build-confd egg-info
	docker pull n3llyb0y/wait
	docker pull rabbitmq

build-confd:
	docker build -t xivo/xivo-confd ..
	docker build --no-cache -t xivo-confd-test -f Dockerfile ..

build-postgres:
	docker pull postgres:9.1
	docker build -t xivo/xivo-postgres -f $(POSTGRES_DOCKER) $(MANAGE_DB_DIR)

build-provd:
	docker build -t xivo/xivo-provd $(PROVD_DIR)

stop:
	cd assets/base && \
	docker-compose kill && \
	docker-compose rm -f

start:
	cd assets/base && \
	docker-compose run --service-ports --rm testdeps && \
	docker-compose run --service-ports --rm tests

test:
	nosetests suite

distclean:
	docker rmi xivo/xivo-provd
	docker rmi xivo/xivo-postgres
	docker rmi xivo/xivo-confd
	docker rmi xivo-confd-test

egg-info:
	cd .. && python setup.py egg_info
