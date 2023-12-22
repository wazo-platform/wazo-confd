PROVD_DIR ?= ../../provd/

ifeq ($(MANAGE_DB_DIR),)
	UPDATE_DB_TARGET=update-db-pull
else
	UPDATE_DB_TARGET=update-db-build
	POSTGRES_DOCKER=$(MANAGE_DB_DIR)/contribs/docker/wazo-confd-db-test/Dockerfile
endif

test-setup: egg-info build-confd update-db

build-confd:
	docker build -t wazoplatform/wazo-confd ..
	docker build --no-cache -t wazo-confd-test -f Dockerfile ..

update-db: $(UPDATE_DB_TARGET)

update-db-pull:
	docker pull wazoplatform/wazo-confd-db-test
	docker tag wazoplatform/wazo-confd-db-test:latest wazoplatform/wazo-confd-db-test:local

update-db-build:
	docker build --pull --no-cache -t wazoplatform/wazo-confd-db-test:local -f $(POSTGRES_DOCKER) $(MANAGE_DB_DIR)

build-provd:
	docker build -t wazoplatform/wazo-provd $(PROVD_DIR)

test:
	pytest -x

egg-info:
	cd .. && python setup.py egg_info

.PHONY: test-setup test egg-info update-db update-db-build update-db-pull build-provd build-confd
