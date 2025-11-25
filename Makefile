VERSION ?= v0.8.10.4
DIST    ?= "uhppoted-app-home-assistant_$(VERSION)"

.PHONY: docker
.PHONY: update

SHARE="/usr/local/etc/com.github.uhppoted/home-assistant"

update:
	@echo "update: nothing to do"

update-release:
	@echo "update-release: nothing to do"

format: 
	. .venv/bin/activate && yapf -ri custom_components/uhppoted
	. .venv/bin/activate && yapf -ri tests

translate:
	python3 -m script.translations develop

build: format

test: build
	source .tests/bin/activate && python3 -m unittest tests/uhppoted/*.py 

build-all: format

release: build-all
	rm -rf dist/*
	mkdir -p dist/$(DIST)
	rsync -av --delete \
          --exclude '.DS_Store'   \
          --exclude '__pycache__' \
          --exclude '.style.yapf' \
          custom_components/uhppoted dist/$(DIST)/
	tar --directory=dist/$(DIST) --exclude=".DS_Store" -cvzf dist/$(DIST)-alpha.tar.gz uhppoted
	cd dist/$(DIST); zip -x .DS_Store --recurse-paths ../$(DIST)-alpha.zip .
	cd dist/$(DIST); zip -x .DS_Store --recurse-paths ../uhppoted.zip .

publish: release
	echo "Releasing version $(VERSION)"
	rm -rf dist/development
	rm -f dist/development.tar.gz
	rm -f dist/development.zip
	gh release create "$(VERSION)" \
	                  "./dist/uhppoted-app-home-assistant_$(VERSION)-alpha.tar.gz" \
	                  "./dist/uhppoted-app-home-assistant_$(VERSION)-alpha.zip" \
	                  --draft --prerelease --title "$(VERSION)-alpha" --notes-file release-notes.md

docker-build:
	docker run --detach --name home-assistant --restart=unless-stopped --publish 8123:8123 \
               --env "TZ=America/New York" \
               --mount type=bind,source=$(SHARE),target=/config \
               ghcr.io/home-assistant/home-assistant:stable

docker-hass:
	docker start home-assistant

docker-hass-it:
	docker exec -it home-assistant bash

docker:
	cd docker/dev/stable && docker compose up --build

docker-restart:
	docker restart home-assistant-stable && docker logs -f home-assistant-stable

docker-2024.11.3:
	cd docker/dev/2024.11.3 && docker compose up --build

# hass:
# 	hass -c config


swipe:
	curl -X POST "http://127.0.0.1:8000/uhppote/simulator/405419896/swipe" -H "accept: application/json" -H "Content-Type: application/json" -d '{"door":1,"card-number":8165535,"direction":1}'

swipe2:
	curl -X POST "http://127.0.0.1:8000/uhppote/simulator/405419896/swipe" -H "accept: application/json" -H "Content-Type: application/json" -d '{"door":3,"card-number":8165536,"direction":1}'

open:
	curl -X POST "http://127.0.0.1:8000/uhppote/simulator/405419896/door/1" -H "accept: application/json" -H "Content-Type: application/json" -d '{"action":"open"}'

close:
	curl -X POST "http://127.0.0.1:8000/uhppote/simulator/405419896/door/1" -H "accept: application/json" -H "Content-Type: application/json" -d '{"action":"close"}'

button:
	curl -X POST "http://127.0.0.1:8000/uhppote/simulator/405419896/door/1" -H "accept: application/json" -H "Content-Type: application/json" -d '{"action":"button", "duration":15}'

emulator:
	cd docker && docker compose up

