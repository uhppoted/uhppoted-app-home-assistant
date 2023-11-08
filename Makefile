.PHONY: docker

hass:
	hass -c config

docker-build:
	docker run -d --name home-assistant --restart=unless-stopped -p 8123:8123 \
               -e TZ=America/Vancouver \
               -v /usr/local/etc/com.github.uhppoted/home-assistant:/config \
               ghcr.io/home-assistant/home-assistant:stable

docker-run:
	docker start home-assistant

docker-hass:
	docker exec -it home-assistant bash
