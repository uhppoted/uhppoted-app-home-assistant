DIST ?= development

.PHONY: docker

SHARE="/usr/local/etc/com.github.uhppoted/home-assistant"

format: 
	yapf -ri custom_components/uhppoted
#	yapf -ri tests

translate:
	python3 -m script.translations develop

build: format

build-all: format

release: build-all
	mkdir -p dist/$(DIST)
	rsync -av --delete \
          --exclude '.DS_Store'   \
          --exclude '__pycache__' \
          --exclude '.style.yapf' \
          custom_components/uhppoted dist/$(DIST)/
	tar --directory=dist/$(DIST) --exclude=".DS_Store" -cvzf dist/$(DIST).tar.gz uhppoted
#	cd dist; zip --recurse-paths $(DIST).zip $(DIST)

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

