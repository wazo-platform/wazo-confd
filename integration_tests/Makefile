.PHONY: test-setup distclean

PROVD_DIR ?= ../../provisioning
MANAGE_DB_DIR ?= ../../manage-db/
POSTGRES_DOCKER=$(MANAGE_DB_DIR)/contribs/postgres-test/Dockerfile


test-setup: build-provd build-confd egg-info
	docker pull n3llyb0y/wait
	docker pull rabbitmq
	docker pull wazopbx/postgres
	docker pull wazopbx/postgres-test
	docker pull wazopbx/xivo-auth-mock
	docker pull p0bailey/docker-flask
	docker pull swaggerapi/swagger-validator

build-confd:
	docker build -t wazopbx/xivo-confd ..
	docker build --no-cache -t xivo-confd-test -f Dockerfile ..

update-db:
	docker build --no-cache -t wazopbx/postgres-test -f $(POSTGRES_DOCKER) $(MANAGE_DB_DIR)

build-provd:
	docker build -t wazopbx/xivo-provd $(PROVD_DIR)

stop:
	cd assets/base && \
	docker-compose kill && \
	docker-compose rm -f

start:
	cd assets/base && \
	docker-compose run --service-ports --rm tests

test:
	nosetests suite

distclean:
	docker rmi xivo/xivo-provd
	docker rmi xivo/postgres-test
	docker rmi xivo/xivo-confd
	docker rmi xivo-confd-test

egg-info:
	cd .. && python setup.py egg_info
