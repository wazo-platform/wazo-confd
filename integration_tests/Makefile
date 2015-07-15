.PHONY: test-image test-setup distclean

PROVD_DIR=../../xivo-provisioning
MANAGE_DB_DIR=../../xivo-manage-db/
POSTGRES_DOCKER=$(MANAGE_DB_DIR)/contribs/xivo-postgres/Dockerfile


test-setup:
	docker build -t xivo/xivo-provd $(PROVD_DIR)
	docker build -t xivo/xivo-postgres -f $(POSTGRES_DOCKER) $(MANAGE_DB_DIR)
	docker build -t xivo/xivo-confd ..
	docker pull n3llyb0y/wait
	docker pull rabbitmq

test-image:
	docker build --no-cache -t xivo-confd-test -f Dockerfile ..

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
