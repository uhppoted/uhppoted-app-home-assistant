VERSION ?= 0.8.8.1
DIST    ?= development

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
	cd dist/$(DIST); zip -x .DS_Store --recurse-paths ../$(DIST).zip .

publish: release
	echo "Releasing version $(VERSION)"
	rm -rf dist/development
	rm -f dist/development.tar.gz
	rm -f dist/development.zip
	gh release create "$(VERSION)" "./dist/uhppote-app-home-assistant_$(VERSION)-alpha.tar.gz"  "./dist/uhppote-app-home-assistant_$(VERSION)-alpha.zip" --draft --prerelease --title "$(VERSION)-alpha" --notes-file release-notes.md

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


swipe:
	curl -X POST "http://127.0.0.1:8000/uhppote/simulator/405419896/swipe" -H "accept: application/json" -H "Content-Type: application/json" -d '{"door":1,"card-number":8165535,"direction":1}'

open:
	curl -X POST "http://127.0.0.1:8000/uhppote/simulator/405419896/door/1" -H "accept: application/json" -H "Content-Type: application/json" -d '{"action":"open"}'

close:
	curl -X POST "http://127.0.0.1:8000/uhppote/simulator/405419896/door/1" -H "accept: application/json" -H "Content-Type: application/json" -d '{"action":"close"}'

button:
	curl -X POST "http://127.0.0.1:8000/uhppote/simulator/405419896/door/1" -H "accept: application/json" -H "Content-Type: application/json" -d '{"action":"button", "duration":15}'

emulator:
	cd docker && docker compose up

