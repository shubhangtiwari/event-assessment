PORT := 2408
SHELL := /bin/bash

# Load .env if present so ADMIN_PASSWORD (and any other overrides) are picked up.
ifneq (,$(wildcard .env))
    include .env
    export
endif

.PHONY: install start start-cf tunnel

install:
	uv sync --quiet

start: install
	PORT=$(PORT) uv run python app.py

start-cf: install
	@echo "Starting Flask (localhost:$(PORT)) + Cloudflare quick tunnel. Ctrl+C stops both."
	@trap 'kill 0' EXIT INT TERM; \
		PORT=$(PORT) uv run python app.py & \
		sleep 2 && cloudflared tunnel --url http://localhost:$(PORT)

tunnel:
	cloudflared tunnel --url http://localhost:$(PORT)
