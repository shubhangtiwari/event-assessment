PORT := 2408
SHELL := /bin/bash

# Load .env if present so ADMIN_PASSWORD (and any other overrides) are picked up.
ifneq (,$(wildcard .env))
    include .env
    export
endif

.PHONY: start start-cf install app tunnel tunnel-cf

start: install
	@echo "Starting Flask (localhost:$(PORT)) + ngrok tunnel. Ctrl+C stops both."
	@trap 'kill 0' EXIT INT TERM; \
		PORT=$(PORT) uv run python app.py & \
		sleep 2 && ngrok http --url=$(NGROK_DOMAIN) $(PORT) --log=stdout & \
		wait

install:
	uv sync --quiet

app: install
	PORT=$(PORT) uv run python app.py

tunnel:
	ngrok http --url=$(NGROK_DOMAIN) $(PORT)

start-cf: install
	@echo "Starting Flask (localhost:$(PORT)) + Cloudflare quick tunnel. Ctrl+C stops both."
	@trap 'kill 0' EXIT INT TERM; \
		PORT=$(PORT) uv run python app.py & \
		sleep 2 && cloudflared tunnel --url http://localhost:$(PORT) 2>&1 \
			| tee >(uv run python scripts/capture_tunnel_url.py) & \
		wait

tunnel-cf:
	cloudflared tunnel --url http://localhost:$(PORT)
