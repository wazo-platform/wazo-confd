PROVD_DIR ?= ../../provd/
MANAGE_DB_DIR ?= ../../manage-db/
POSTGRES_DOCKER=$(MANAGE_DB_DIR)/contribs/docker/wazo-confd-db-test/Dockerfile

test-setup: egg-info build-confd

build-confd:
	docker build -t wazoplatform/wazo-confd ..
	docker build --no-cache -t wazo-confd-test -f Dockerfile ..

update-db:
	docker build --no-cache -t wazoplatform/wazo-confd-db-test -f $(POSTGRES_DOCKER) $(MANAGE_DB_DIR)

build-provd:
	docker build -t wazoplatform/wazo-provd $(PROVD_DIR)

test:
	nosetests -x

egg-info:
	cd .. && python setup.py egg_info

.PHONY: test-setup test egg-info update-db build-provd build-confd
