.PHONY: docker

SHARE="/usr/local/etc/com.github.uhppoted/home-assistant"

format: 
	yapf -ri custom_components/uhppoted
#	yapf -ri tests

build: format

build-all: format

docker-build:
	docker run --detach --name home-assistant --restart=unless-stopped --publish 8123:8123 \
               --env TZ=America/New York \
               --mount type=bind,source=$(SHARE),target=/config \
               ghcr.io/home-assistant/home-assistant:stable

docker-run:
	docker start home-assistant

docker-hass:
	docker exec -it home-assistant bash

# hass:
# 	hass -c config

