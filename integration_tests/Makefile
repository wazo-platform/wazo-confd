.PHONY: test-setup test egg-info update-db build-provd build-confd

PROVD_DIR ?= ../../provisioning
MANAGE_DB_DIR ?= ../../manage-db/
POSTGRES_DOCKER=$(MANAGE_DB_DIR)/contribs/postgres-test/Dockerfile


test-setup: egg-info build-confd
	docker pull wazopbx/wait
	docker pull rabbitmq
	docker pull wazopbx/postgres
	docker pull wazopbx/postgres-test
	docker pull wazopbx/wazo-auth-mock
	docker pull wazopbx/xivo-provd
	docker pull p0bailey/docker-flask
	docker pull swaggerapi/swagger-validator

build-confd:
	docker build -t wazopbx/xivo-confd ..
	docker build --no-cache -t xivo-confd-test -f Dockerfile ..

update-db:
	docker build --no-cache -t wazopbx/postgres-test -f $(POSTGRES_DOCKER) $(MANAGE_DB_DIR)

build-provd:
	docker build -t wazopbx/xivo-provd $(PROVD_DIR)

test:
	nosetests

egg-info:
	cd .. && python setup.py egg_info
