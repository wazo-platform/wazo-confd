.PHONY: test-image test-setup clean sync-context

PROVD_DIR=../../xivo-provisioning

test-setup:
	docker build -t xivo/xivo-confd ..
	docker build -t xivo/xivo-provd $(PROVD_DIR)
	docker pull n3llyb0y/wait
	docker pull postgres:9.1
	docker pull rabbitmq

test-image:
	docker build --no-cache -t xivo-confd-test -f Dockerfile ..

test: test_image
	nosetest suite
