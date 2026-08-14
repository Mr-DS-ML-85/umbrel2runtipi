#!/usr/bin/env python3
"""
Convert Umbrel App Store apps to Runtipi-compatible appstore format.

- Reads the cloned Umbrel apps repo (umbrel-apps/)
- Reads the cloned Runtipi official appstore (runtipi-official/)
- Dedupes: skips any Umbrel app that already exists in the Runtipi registry
  (match by id, normalized id, or normalized name)
- Skips apps that fundamentally depend on Umbrel's own infrastructure
  (Bitcoin/Lightning/Electrs/Monero tor-integrated system apps, tor-only apps)
- Converts each remaining app:
    umbrel-app.yml       -> config.json
    docker-compose.yml   -> dynamic docker-compose.yml (x-runtipi schema v2)
    description          -> metadata/description.md
    gallery icon (SVG)   -> metadata/logo.jpg
- Writes the store into <out>/apps/<app-id>/... plus a report.

Usage: python3 convert.py
"""

from __future__ import annotations

import io
import json
import os
import re
import shutil
import time
import urllib.request
from pathlib import Path

import yaml

# --- YAML 1.2-compatible loader ------------------------------------------
# Docker Compose (go-yaml v3) follows YAML 1.2: plain scalars like "10025:25"
# stay strings. PyYAML's default resolver is YAML 1.1 and would interpret
# "10025:25" as a base-60 integer (601525), corrupting port mappings.
# Build a loader with a strict decimal int/float resolver.
_INT = re.compile(r"^[-+]?[0-9]+$")
_FLOAT = re.compile(
    r"^[-+]?(?:[0-9]+\.[0-9]*|[0-9]*\.[0-9]+|[0-9]+[eE][-+]?[0-9]+"
    r"|[0-9]+\.[0-9]*[eE][-+]?[0-9]+)$"
)


class ComposeLoader(yaml.SafeLoader):
    pass


def _build_resolvers():
    base = {k: list(v) for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()}
    for ch in base:
        base[ch] = [
            (t, rx)
            for t, rx in base[ch]
            if t not in ("tag:yaml.org,2002:int", "tag:yaml.org,2002:float")
        ]
    for ch in "0123456789":
        base.setdefault(ch, []).append(("tag:yaml.org,2002:int", _INT))
        base.setdefault(ch, []).append(("tag:yaml.org,2002:float", _FLOAT))
    for ch in "+-":
        base.setdefault(ch, []).append(("tag:yaml.org,2002:int", _INT))
        base.setdefault(ch, []).append(("tag:yaml.org,2002:float", _FLOAT))
    return base


ComposeLoader.yaml_implicit_resolvers = _build_resolvers()

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
UMBREL_REPO = ROOT_DIR / "umbrel-apps"
RUNTIPI_REPO = ROOT_DIR / "runtipi-official"
OUT_DIR = ROOT_DIR
REPORT_PATH = ROOT_DIR / "conversion-report.md"

ICON_BASE = "https://getumbrel.github.io/umbrel-apps-gallery"

# Repo logo fallbacks for apps whose Umbrel gallery icon is broken (renders
# all-black, e.g. the gallery PNG was flattened without its alpha). Value is a
# raw.githubusercontent.com URL to the app's real logo.
REPO_LOGO_FALLBACKS = {
    "route96": "https://raw.githubusercontent.com/v0l/route96/main/ui_src/public/route96.jpg",
    "fizzy": "https://raw.githubusercontent.com/basecamp/fizzy/main/public/app-icon.png",
    "dokploy": "https://raw.githubusercontent.com/Dokploy/dokploy/main/apps/dokploy/public/logo.svg",
    "coolify": "https://raw.githubusercontent.com/coollabsio/coolify/main/public/coolify-logo.svg",
    "pterodactyl": "https://raw.githubusercontent.com/pterodactyl/panel/master/public/assets/svgs/pterodactyl.svg",
}

# Manual overrides for apps whose Umbrel package depends on Umbrel install
# hooks / templates and therefore cannot be converted mechanically, but that DO
# have an official upstream image configurable via plain environment variables.
# Each entry is a fully hand-written compose; the config.json form fields are
# generated from MANUAL_OTBR_FORM_FIELDS below.
#
# openthread-border-router:
#   The Umbrel package mounts ${APP_DATA_DIR}/server.py (rendered from a
#   template by Umbrel's install hook) and waits for settings.env written by its
#   pre-start hook. Neither exists on Runtipi. The official openthread/border-router
#   image instead configures the radio + interfaces purely through env vars
#   (OT_RCP_DEVICE, OT_INFRA_IF, OT_WEB_LISTEN_PORT, OT_REST_LISTEN_PORT, ...),
#   so it works on Runtipi with no hooks.
MANUAL_COMPOSES = {
    "openthread-border-router": {
        "compose": {
            "services": {
                "otbr": {
                    "image": "openthread/border-router:latest",
                    "container_name": "openthread-border-router",
                    "restart": "unless-stopped",
                    "network_mode": "host",
                    "privileged": True,
                    "environment": [
                        "OT_LOG_LEVEL=${OT_LOG_LEVEL}",
                        "OT_RCP_DEVICE=${OT_RCP_DEVICE}",
                        "OT_INFRA_IF=${OT_INFRA_IF}",
                        "OT_THREAD_IF=${OT_THREAD_IF}",
                        "OT_WEB_LISTEN_ADDR=${OT_WEB_LISTEN_ADDR}",
                        "OT_WEB_LISTEN_PORT=${OT_WEB_LISTEN_PORT}",
                        "OT_REST_LISTEN_ADDR=${OT_REST_LISTEN_ADDR}",
                        "OT_REST_LISTEN_PORT=${OT_REST_LISTEN_PORT}",
                    ],
                    "volumes": [
                        "${APP_DATA_DIR}/data:/data",
                        "/dev:/dev:ro",
                    ],
                    "labels": {
                        "runtipi.managed": "true",
                    },
                    "x-runtipi": {
                        "internal_port": 7587,
                        "is_main": True,
                    },
                }
            }
        },
        "x-runtipi": {"schema_version": 2},
        "port": 7587,  # otbr-web GUI (OT_WEB_LISTEN_PORT), host networking
    },
}

# Compose env-var values to rewrite for specific apps after conversion. Keyed
# by app id -> service name -> env var -> new value. Needed when the Umbrel
# package wires secrets together but the app hard-validates them (mailflow:
# SESSION_SECRET >= 32 chars, ENCRYPTION_KEY exactly 64 hex chars).
MANUAL_ENV_OVERRIDES = {
    "mailflow": {
        "backend": {
            "SESSION_SECRET": "${SESSION_SECRET}",
            "ENCRYPTION_KEY": "${ENCRYPTION_KEY}",
        },
    },
}


def apply_env_overrides(compose: dict, app_id: str) -> None:
    overrides = MANUAL_ENV_OVERRIDES.get(app_id)
    if not overrides:
        return
    services = compose.get("services", {}) or {}
    for svc_name, env_map in overrides.items():
        svc = services.get(svc_name)
        if not svc:
            continue
        env = svc.get("environment")
        if isinstance(env, dict):
            for k, v in env_map.items():
                if k in env:
                    env[k] = v
        elif isinstance(env, list):
            for i, e in enumerate(env):
                if isinstance(e, str) and "=" in e:
                    k, _, val = e.partition("=")
                    if k.strip() in env_map:
                        env[i] = f"{k.strip()}={env_map[k.strip()]}"


MANUAL_FORM_FIELDS = {
    "mailflow": [
        {
            "label": "Session secret",
            "type": "random",
            "env_variable": "SESSION_SECRET",
            "min": 32,
            "required": False,
            "hint": "Must be at least 32 characters.",
        },
        {
            "label": "Encryption key",
            "type": "random",
            "env_variable": "ENCRYPTION_KEY",
            "encoding": "hex",
            "min": 64,
            "required": False,
            "hint": "Exactly 64 hex characters (32 bytes).",
        },
    ],
    "openthread-border-router": [
        {
            "label": "Thread radio device",
            "type": "text",
            "env_variable": "OT_RCP_DEVICE",
            "required": True,
            "hint": "e.g. spinel+hdlc+uart:///dev/ttyACM0?uart-baudrate=1000000",
        },
        {
            "label": "Backbone network interface",
            "type": "text",
            "env_variable": "OT_INFRA_IF",
            "required": True,
            "hint": "The host network interface to bridge Thread to, e.g. eth0",
        },
        {
            "label": "Thread interface",
            "type": "text",
            "env_variable": "OT_THREAD_IF",
            "required": False,
            "default": "wpan0",
        },
        {
            "label": "Web GUI listen address",
            "type": "text",
            "env_variable": "OT_WEB_LISTEN_ADDR",
            "required": False,
            "default": "0.0.0.0",
        },
        {
            "label": "Web GUI port",
            "type": "number",
            "env_variable": "OT_WEB_LISTEN_PORT",
            "required": False,
            "default": "7587",
        },
        {
            "label": "REST API listen address",
            "type": "text",
            "env_variable": "OT_REST_LISTEN_ADDR",
            "required": False,
            "default": "0.0.0.0",
        },
        {
            "label": "REST API port",
            "type": "number",
            "env_variable": "OT_REST_LISTEN_PORT",
            "required": False,
            "default": "8083",
        },
        {
            "label": "Log level",
            "type": "number",
            "env_variable": "OT_LOG_LEVEL",
            "required": False,
            "default": "7",
        },
    ],
}

# Extra apps that are NOT in the Umbrel catalogue but are popular self-hosted
# apps the user asked to add. They are hand-written, Runtipi-compatible, and
# injected after the main conversion loop (the write step wipes apps/, so they
# must be part of `converted`). Each entry supplies a full compose, manifest,
# config overrides (port/exposable/form_fields) and main_service.
EXTRA_APPS = {
    "dokploy": {
        "port": 3000,
        "exposable": False,
        "main_service": "dokploy",
        "manifest": {
            "id": "dokploy",
            "name": "Dokploy",
            "category": "utilities",
            "tagline": "Self-hosted Platform as a Service (PaaS)",
            "description": (
                "Dokploy is a free, self-hostable Platform as a Service (PaaS) that "
                "simplifies deployment and management of applications, databases and "
                "Docker Compose stacks. It uses Traefik for automatic HTTPS routing.\n\n"
                "It manages Docker directly through the host socket and runs its control "
                "plane in Docker Swarm mode, so the host Docker engine must be reachable "
                "and able to run Swarm services. Dokploy also brings up its own Traefik on "
                "ports 80/443, which will conflict with Runtipi's Traefik -- expose Dokploy "
                "on a host with those ports free, or stop Runtipi's proxy while using it."
            ),
            "developer": "Dokploy",
            "repo": "https://github.com/Dokploy/dokploy",
            "website": "https://dokploy.com",
            "version": "0.29.14",
            "port": 3000,
        },
        "form_fields": [
            {
                "label": "Database password",
                "type": "random",
                "env_variable": "APP_DB_PASSWORD",
                "min": 32,
                "required": False,
            },
        ],
        "compose": {
            "services": {
                "dokploy": {
                    "image": "dokploy/dokploy:0.29.14",
                    "container_name": "dokploy",
                    "restart": "unless-stopped",
                    "ports": ["${APP_PORT}:3000"],
                    "volumes": [
                        "/var/run/docker.sock:/var/run/docker.sock",
                        "/etc/dokploy:/etc/dokploy",
                        "${APP_DATA_DIR}/docker:/root/.docker",
                    ],
                    "environment": [
                        "POSTGRES_PASSWORD=${APP_DB_PASSWORD}",
                        "DATABASE_URL=postgres://dokploy:${APP_DB_PASSWORD}@dokploy-postgres:5432/dokploy",
                    ],
                    "depends_on": {
                        "dokploy-postgres": {"condition": "service_healthy"},
                    },
                    "networks": ["tipi_main_network"],
                    "labels": {
                        "runtipi.managed": "true",
                    },
                    "x-runtipi": {"internal_port": 3000, "is_main": True},
                },
                "dokploy-postgres": {
                    "image": "postgres:16-alpine",
                    "container_name": "dokploy-postgres",
                    "restart": "unless-stopped",
                    "environment": [
                        "POSTGRES_USER=dokploy",
                        "POSTGRES_PASSWORD=${APP_DB_PASSWORD}",
                        "POSTGRES_DB=dokploy",
                    ],
                    "volumes": ["${APP_DATA_DIR}/postgres:/var/lib/postgresql/data"],
                    "healthcheck": {
                        "test": ["CMD-SHELL", "pg_isready -U dokploy -d dokploy"],
                        "interval": "5s",
                        "retries": 10,
                        "timeout": "2s",
                    },
                    "networks": ["tipi_main_network"],
                    "labels": {"runtipi.managed": "true"},
                },
            },
        },
        "x-runtipi": {"schema_version": 2},
    },
    "coolify": {
        "port": 8000,
        "exposable": True,
        "main_service": "coolify",
        "manifest": {
            "id": "coolify",
            "name": "Coolify",
            "category": "utilities",
            "tagline": "Self-hosted Heroku / Netlify alternative",
            "description": (
                "Coolify is an open-source, self-hostable Platform as a Service (PaaS) "
                "alternative to Vercel, Heroku and Railway. Deploy applications, databases "
                "and Docker Compose stacks from git, Docker images or templates with automatic "
                "SSL, all through a web UI.\n\n"
                "It manages the host Docker engine through the socket. For realtime features "
                "the optional `soketi` service is omitted in this packaging; the dashboard and "
                "deployments work without it."
            ),
            "developer": "coolLabs",
            "repo": "https://github.com/coollabsio/coolify",
            "website": "https://coolify.io",
            "version": "4.3.2",
            "port": 8000,
        },
        "form_fields": [
            {
                "label": "Database password",
                "type": "random",
                "env_variable": "APP_DB_PASSWORD",
                "min": 32,
                "required": False,
            },
            {
                "label": "Redis password",
                "type": "random",
                "env_variable": "APP_REDIS_PASSWORD",
                "min": 32,
                "required": False,
            },
            {
                "label": "App encryption key (Laravel APP_KEY)",
                "type": "random",
                "env_variable": "APP_KEY",
                "min": 32,
                "required": False,
            },
        ],
        "compose": {
            "services": {
                "coolify": {
                    "image": "ghcr.io/coollabsio/coolify:4.3.2",
                    "container_name": "coolify",
                    "restart": "unless-stopped",
                    "ports": ["${APP_PORT}:8080"],
                    "volumes": [
                        "/var/run/docker.sock:/var/run/docker.sock",
                        "${APP_DATA_DIR}/data:/data",
                        "${APP_DATA_DIR}/data/ssh:/var/www/html/storage/app/ssh",
                        "${APP_DATA_DIR}/data/applications:/var/www/html/storage/app/applications",
                        "${APP_DATA_DIR}/data/databases:/var/www/html/storage/app/databases",
                        "${APP_DATA_DIR}/data/services:/var/www/html/storage/app/services",
                        "${APP_DATA_DIR}/data/backups:/var/www/html/storage/app/backups",
                    ],
                    "environment": [
                        "APP_ENV=production",
                        "DB_CONNECTION=pgsql",
                        "DB_HOST=postgres",
                        "DB_PORT=5432",
                        "DB_DATABASE=coolify",
                        "DB_USERNAME=coolify",
                        "DB_PASSWORD=${APP_DB_PASSWORD}",
                        "DATABASE_URL=postgres://coolify:${APP_DB_PASSWORD}@postgres:5432/coolify",
                        "REDIS_HOST=redis",
                        "REDIS_PASSWORD=${APP_REDIS_PASSWORD}",
                        "APP_KEY=${APP_KEY}",
                    ],
                    "depends_on": {
                        "postgres": {"condition": "service_healthy"},
                        "redis": {"condition": "service_healthy"},
                    },
                    "networks": ["tipi_main_network"],
                    "labels": {
                        "runtipi.managed": "true",
                    },
                    "x-runtipi": {"internal_port": 8080, "is_main": True},
                },
                "postgres": {
                    "image": "postgres:16-alpine",
                    "container_name": "coolify-postgres",
                    "restart": "unless-stopped",
                    "environment": [
                        "POSTGRES_USER=coolify",
                        "POSTGRES_PASSWORD=${APP_DB_PASSWORD}",
                        "POSTGRES_DB=coolify",
                    ],
                    "volumes": ["${APP_DATA_DIR}/postgres:/var/lib/postgresql/data"],
                    "healthcheck": {
                        "test": ["CMD-SHELL", "pg_isready -U coolify -d coolify"],
                        "interval": "5s",
                        "retries": 10,
                        "timeout": "2s",
                    },
                    "networks": ["tipi_main_network"],
                    "labels": {"runtipi.managed": "true"},
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "container_name": "coolify-redis",
                    "restart": "unless-stopped",
                    "command": "redis-server --requirepass ${APP_REDIS_PASSWORD}",
                    "volumes": ["${APP_DATA_DIR}/redis:/data"],
                    "healthcheck": {
                        "test": ["CMD-SHELL", "redis-cli -a ${APP_REDIS_PASSWORD} ping | grep PONG"],
                        "interval": "5s",
                        "retries": 10,
                        "timeout": "2s",
                    },
                    "networks": ["tipi_main_network"],
                    "labels": {"runtipi.managed": "true"},
                },
            },
        },
        "x-runtipi": {"schema_version": 2},
    },
    "pterodactyl": {
        "port": 8082,
        "exposable": True,
        "main_service": "pterodactyl-panel",
        "manifest": {
            "id": "pterodactyl",
            "name": "Pterodactyl",
            "category": "utilities",
            "tagline": "Open-source game server management panel",
            "description": (
                "Pterodactyl is an open-source game server management panel. It provides a "
                "web UI to deploy, manage and monitor game servers (Minecraft, Terraria, CS2, ...) "
                "across multiple nodes, with an integrated account system, server resource "
                "limits and a REST API.\n\n"
                "**After install**, the panel needs one manual step before you can log in: create "
                "the admin user by running inside the panel container:\n\n"
                "```bash\n"
                "docker exec -it pterodactyl-panel php artisan p:user:make\n"
                "```\n\n"
                "This package runs the control *panel* plus its MariaDB and Redis services. The "
                "*wings* daemon that actually hosts game servers is a separate component that "
                "runs on each node, requires a generated config and direct Docker access, and is "
                "not included here -- see https://pterodactyl.io for setting up wings and "
                "connecting nodes."
            ),
            "developer": "Pterodactyl",
            "repo": "https://github.com/pterodactyl/panel",
            "website": "https://pterodactyl.io",
            "version": "1.15.0",
            "port": 8082,
        },
        "form_fields": [
            {
                "label": "Database password",
                "type": "random",
                "env_variable": "APP_DB_PASSWORD",
                "min": 32,
                "required": False,
            },
            {
                "label": "Database root password",
                "type": "random",
                "env_variable": "APP_DB_ROOT_PASSWORD",
                "min": 32,
                "required": False,
            },
            {
                "label": "Service author email",
                "type": "email",
                "env_variable": "APP_SERVICE_AUTHOR",
                "required": False,
                "default": "noreply@localhost",
            },
            {
                "label": "Timezone",
                "type": "text",
                "env_variable": "APP_TIMEZONE",
                "required": False,
                "default": "UTC",
            },
        ],
        "compose": {
            "services": {
                "pterodactyl-panel": {
                    "image": "ghcr.io/pterodactyl/panel:1.15.0",
                    "container_name": "pterodactyl-panel",
                    "restart": "unless-stopped",
                    "ports": ["${APP_PORT}:80"],
                    "environment": [
                        "APP_ENV=production",
                        "APP_ENVIRONMENT_ONLY=false",
                        "APP_URL=${APP_PROTOCOL:-http}://${APP_DOMAIN}",
                        "APP_TIMEZONE=${APP_TIMEZONE:-UTC}",
                        "APP_SERVICE_AUTHOR=${APP_SERVICE_AUTHOR:-noreply@localhost}",
                        "TRUSTED_PROXIES=*",
                        "DB_HOST=database",
                        "DB_PORT=3306",
                        "DB_DATABASE=panel",
                        "DB_USERNAME=pterodactyl",
                        "DB_PASSWORD=${APP_DB_PASSWORD}",
                        "CACHE_DRIVER=redis",
                        "SESSION_DRIVER=redis",
                        "QUEUE_DRIVER=redis",
                        "REDIS_HOST=cache",
                        "REDIS_PORT=6379",
                        "REDIS_PASSWORD=null",
                        "HASHIDS_LENGTH=8",
                        "MAIL_FROM=${APP_SERVICE_AUTHOR:-noreply@localhost}",
                        "MAIL_DRIVER=smtp",
                        "MAIL_HOST=localhost",
                        "MAIL_PORT=1025",
                        "MAIL_USERNAME=",
                        "MAIL_PASSWORD=",
                        "MAIL_ENCRYPTION=true",
                    ],
                    "depends_on": {
                        "database": {"condition": "service_healthy"},
                        "cache": {"condition": "service_healthy"},
                    },
                    "volumes": [
                        "${APP_DATA_DIR}/var:/app/var",
                        "${APP_DATA_DIR}/nginx:/etc/nginx/http.d",
                        "${APP_DATA_DIR}/certs:/etc/letsencrypt",
                        "${APP_DATA_DIR}/logs:/app/storage/logs",
                    ],
                    "networks": ["tipi_main_network"],
                    "labels": {
                        "runtipi.managed": "true",
                    },
                    "healthcheck": {
                        "test": ["CMD-SHELL", "wget -qO/dev/null http://127.0.0.1/ || exit 1"],
                        "interval": "30s",
                        "timeout": "5s",
                        "retries": 5,
                        "start_period": "60s",
                    },
                    "x-runtipi": {"internal_port": 80, "is_main": True},
                },
                "database": {
                    "image": "mariadb:11",
                    "container_name": "pterodactyl-database",
                    "restart": "unless-stopped",
                    "environment": [
                        "MYSQL_DATABASE=panel",
                        "MYSQL_USER=pterodactyl",
                        "MYSQL_PASSWORD=${APP_DB_PASSWORD}",
                        "MYSQL_ROOT_PASSWORD=${APP_DB_ROOT_PASSWORD}",
                    ],
                    "volumes": ["${APP_DATA_DIR}/mysql:/var/lib/mysql"],
                    "networks": ["tipi_main_network"],
                    "labels": {
                        "runtipi.managed": "true",
                    },
                    "healthcheck": {
                        "test": ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"],
                        "interval": "10s",
                        "timeout": "5s",
                        "retries": 10,
                    },
                },
                "cache": {
                    "image": "redis:alpine",
                    "container_name": "pterodactyl-cache",
                    "restart": "unless-stopped",
                    "volumes": ["${APP_DATA_DIR}/redis:/data"],
                    "networks": ["tipi_main_network"],
                    "labels": {
                        "runtipi.managed": "true",
                    },
                    "healthcheck": {
                        "test": ["CMD", "redis-cli", "ping"],
                        "interval": "10s",
                        "timeout": "3s",
                        "retries": 5,
                    },
                },
            },
        },
        "x-runtipi": {"schema_version": 2},
    },
}

# Host ports already in use on the user's server (nmap result) - the store must
# NEVER assign these to an app. Edit this list to match your setup.
RESERVED_PORTS = {
    22, 25, 53, 80, 139, 143, 443, 445, 465, 587, 631, 993,
    2000, 2283, 2285, 3007, 3478, 4190, 8043, 8081, 8089, 8099,
    8104, 8152, 8250, 8374, 8443, 8642, 8840, 8999, 9119, 9983, 45876,
}

RUNTIPI_SYSTEM_VARS = {
    "APP_DATA_DIR", "APP_PORT", "APP_DOMAIN", "APP_PROTOCOL", "APP_ID",
    "APP_VERSION", "TZ", "UID", "GID", "RUNTIPI_MEDIA_DIR", "RUNTIPI_APP_ID",
    "LOCAL_DOMAIN", "ROOT_FOLDER_HOST", "APP_EXPOSED", "DNS_IP",
}

# Umbrel system-app dependencies => these apps cannot run on Runtipi without
# Umbrel's own Bitcoin/Lightning infrastructure. If a compose references any of
# these env vars, the app needs an Umbrel system app to provide them.
UMBREL_INFRA_PREFIXES = (
    "APP_BITCOIN", "APP_LIGHTNING", "APP_LND", "APP_LNDG", "APP_CORE_LIGHTNING",
    "APP_ELECTRS", "APP_ELECTRUMX", "APP_FULCRUM", "APP_MEMPOOL", "APP_ELEMENTS",
    "APP_LIBRE_RELAY", "APP_MONERO", "APP_SUREDBITS", "APP_SQUEAKNODE",
    "APP_TDEX", "APP_SAMOURAI", "APP_ZWALLET", "APP_TAILS", "APP_BOLTZ",
    "APP_RTL", "APP_CANARY", "APP_SPHINX", "APP_PINSERVER", "APP_URBIT",
    "APP_SWH", "APP_HIDDEN_SERVICE", "APP_TOR", "APP_ALBY_LN", "APP_LNMARKETS",
    "APP_LNPLUS", "APP_GHOSTFOLIO", "APP_PEERSWAP", "APP_ITCHYSATS",
    "APP_JOINSTR", "APP_CIRCUITBREAKER", "APP_THUNDERHUB", "APP_TORQ",
    "APP_BLESKOMAT", "APP_LNBITS", "APP_BTCPAY", "APP_ORDINALS", "APP_DATUM",
    "APP_BASSIN", "APP_SIHA", "APP_SWAP", "APP_SV2", "APP_MINER_SENTINEL",
)

SECRET_RE = re.compile(
    r"(PASSWORD|_PASS$|^PASSPHRASE|_PASSPHRASE$|_SEED$|_SECRET|_TOKEN$|"
    r"_KEY$|_KEYS$|_SALT$|_API_KEY$|_MASTER_KEY$|_ENCRYPTION_KEY$|"
    r"_JWT_SECRET$|_APP_KEY$|_VAULT_KEY$|_SIG_KEY$|_SIG_SALT$|"
    r"_ACCESS_TOKEN_SALT$|_DB_PASSWORD$|_REDIS_PASSWORD$|_ROOT_PASSWORD$)"
)

CATEGORY_MAP = {
    "files": "data",
    "bitcoin": "finance",
    "crypto": "finance",
    "networking": "network",
    "media": "media",
    "developer": "development",
    "social": "social",
    "ai": "ai",
    "automation": "automation",
    "finance": "finance",
}

KNOWN_SERVICES = {"app_proxy", "web", "server", "app", "db", "api", "backend", "frontend", "nginx", "worker"}

# Env-var reference detection
VAR_REF_RE = re.compile(r"\$\{([A-Z0-9_]+)(?::-([^}]*))?\}", re.IGNORECASE)
VAR_REF_BARE_RE = re.compile(r"(?<!\$)\$(\$)?([A-Z_][A-Z0-9_]*)")


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower().replace("_", "-"))


def collect_vars(compose: dict, app_id: str) -> tuple[dict[str, bool], set[str]]:
    """Return {VAR: has_default} for every APP_* referenced in compose, and set of all vars."""
    default_map: dict[str, bool] = {}
    found: set[str] = set()

    def scan_str(s: str) -> None:
        for m in VAR_REF_RE.finditer(s):
            name, default = m.group(1), m.group(2)
            if not name.startswith("APP_"):
                continue
            found.add(name)
            has_def = default is not None
            default_map[name] = (default_map.get(name, False)) or has_def
        for m in VAR_REF_BARE_RE.finditer(s):
            if m.group(1):
                continue  # $${ escaped
            name = m.group(2)
            if not name.startswith("APP_"):
                continue
            found.add(name)
            # bare $VAR always has no default
            default_map[name] = default_map.get(name, False)

    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                scan_str(str(k))
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)
        elif isinstance(obj, str):
            scan_str(obj)
        elif obj is not None:
            scan_str(str(obj))

    walk(compose)
    return default_map, found


def find_app_proxy(compose: dict, app_id: str):
    services = compose.get("services", {}) or {}
    ap = services.get("app_proxy")
    if not ap:
        return None, None
    env = ap.get("environment", {}) or {}
    env_list = env if isinstance(env, list) else [
        (k, v) for k, v in env.items()
    ]
    host = None
    port = None
    for e in env_list:
        if isinstance(e, str):
            if e.startswith("APP_HOST"):
                host = e.split("=", 1)[1].strip()
            elif e.startswith("APP_PORT"):
                port = e.split("=", 1)[1].strip()
        elif isinstance(e, (list, tuple)) and len(e) == 2:
            if e[0] == "APP_HOST":
                host = str(e[1])
            elif e[0] == "APP_PORT":
                port = str(e[1])
    return host, port


def derive_main_service(compose: dict, app_id: str, host=None, port=None):
    services = (compose.get("services", {}) or {})

    main = None
    if host:
        # e.g. "paperless_webserver_1" -> webserver ; or "$APP_LNDG_IP"
        m = re.match(rf"^{re.escape(app_id)}_([A-Za-z0-9_-]+)_\d+$", host)
        if m:
            candidate = m.group(1)
            if candidate in services:
                main = candidate
        elif "$" not in host:
            stripped = re.sub(r"_\d+$", "", host)
            candidate = stripped.removeprefix(app_id + "_")
            if candidate in services:
                main = candidate

    if not main:
        # prefer the web-facing service name then the first one
        for name in ("web", "webserver", "ui", "server", "app", "frontend", "main", "proxy", "caddy"):
            if name in services:
                main = name
                break
    if not main:
        non_proxy = [s for s in services if s != "app_proxy"]
        if non_proxy:
            main = non_proxy[0]
    return main, port


def parse_port(value):
    if not value:
        return None
    m = re.search(r"(\d+)", str(value))
    return int(m.group(1)) if m else None


def internal_port_from_ports(service: dict, manifest_port: int):
    ports = service.get("ports") or []
    for p in ports:
        p = str(p).split("/")[0]
        if ":" in p:
            host, container = p.split(":", 1)
            # strip ${APP_PORT} or similar variable
            host_num = parse_port(host)
            container_num = parse_port(container)
            if host_num == manifest_port and container_num:
                return container_num
            if host in ("${APP_PORT}", "$APP_PORT") and container_num:
                return container_num
        else:
            n = parse_port(p)
            if n == manifest_port:
                return n
    return None


def convert_compose(app_id: str, compose: dict, manifest_port: int):
    """Return (new_compose, main_service, internal_port, host_port, notes)."""
    notes: list[str] = []
    comp = json.loads(json.dumps(compose))  # deep copy

    for k in ("version", "name", "configs", "networks"):
        comp.pop(k, None)

    services = comp.setdefault("services", {})
    ap_host, ap_port = find_app_proxy(comp, app_id)
    if "app_proxy" in services:
        del services["app_proxy"]
        notes.append("removed umbrel app_proxy service")

    main_service, ap_port = derive_main_service(comp, app_id, ap_host, ap_port)
    internal_port = None
    host_port = manifest_port

    if not main_service:
        raise RuntimeError("unable to determine main service")

    svc = services[main_service]

    # -- determine internal port -----------------------------------------
    if ap_port is not None:
        internal_port = parse_port(ap_port)
    if internal_port is None and svc.get("network_mode") == "host":
        internal_port = manifest_port
        notes.append("host networking app, internal_port set to umbrel port")
    if internal_port is None:
        # try to find a ports entry whose host side == manifest port
        for p in svc.get("ports") or []:
            ps = str(p).split("/")[0]
            if ":" in ps:
                h, c = ps.split(":", 1)
                hn, cn = parse_port(h), parse_port(c)
                if hn == manifest_port and cn:
                    internal_port = cn
                    break
    if internal_port is None and svc.get("ports"):
        # fall back to first TCP port mapping (the UI)
        for p in svc.get("ports") or []:
            ps = str(p)
            proto = ps.split("/")[-1] if "/" in ps else "tcp"
            if proto != "tcp":
                continue
            if ":" in ps.split("/")[0]:
                h, c = ps.split("/")[0].split(":", 1)
                hn, cn = parse_port(h), parse_port(c)
                if cn:
                    internal_port = cn
                    host_port = hn
                    notes.append(f"ui port inferred from ports mapping {h}:{c}")
                    break
    if internal_port is None:
        internal_port = manifest_port
        notes.append(f"inferred internal_port={internal_port} (no app_proxy APP_PORT found)")

    # -- drop container_name, runtipi manages names -----------------------
    # Map custom container names to service names so references still resolve.
    container_map = {}
    for sname, s in (compose.get("services", {}) or {}).items():
        cn = s.get("container_name")
        if isinstance(cn, str) and cn and cn != sname:
            container_map[cn] = sname
        # umbrel compose auto-names containers <project>_<service>_1 (and
        # <project>-<service>-1). Those hostnames are baked into DATABASE_URL /
        # REDIS_URL etc. and do not resolve on runtipi (project name differs),
        # so rewrite them to the plain service name.
        for alt in (f"{app_id}_{sname}_1", f"{app_id}-{sname}-1"):
            container_map[alt] = sname

    for s in services.values():
        s.pop("container_name", None)
        s.pop("networks", None)
        # env_file paths are generated by Umbrel hooks and won't exist here
        if "env_file" in s:
            notes.append(f"removed env_file ({s['env_file']}) - created by umbrel hooks, not available")
            s.pop("env_file", None)
        # variable-based extra_hosts entries can yield an empty host on runtipi
        if isinstance(s.get("extra_hosts"), list):
            s["extra_hosts"] = [h for h in s["extra_hosts"] if "${" not in str(h) and "$" not in str(h)]
            if not s["extra_hosts"]:
                s.pop("extra_hosts", None)
        # remove depends_on refs to app_proxy
        dep = s.get("depends_on")
        if isinstance(dep, list) and "app_proxy" in dep:
            dep.remove("app_proxy")
        if isinstance(dep, dict):
            dep.pop("app_proxy", None)

    # -- main service port mapping: drop the UI mapping (runtipi adds it) --
    removed_ports = []
    if svc.get("ports"):
        kept = []
        for p in svc["ports"]:
            ps = str(p).split("/")[0]
            if ":" in ps:
                h, _ = ps.split(":", 1)
                hn = parse_port(h)
            else:
                h, hn = ps, parse_port(ps)
            is_ui = (
                h == "${APP_PORT}"
                or h == "$APP_PORT"
                or (hn is not None and hn == host_port)
            )
            if is_ui and (str(p).split("/")[0].count(":") == 1):
                removed_ports.append(str(p))
                continue
            kept.append(p)
        if removed_ports:
            svc["ports"] = kept
            notes.append(f"removed ui port mapping(s) handled by runtipi: {removed_ports}")
        if not svc.get("ports"):
            svc.pop("ports", None)

    # -- rewrite UMBREL_ROOT shared-storage paths --------------------------
    def rewrite_paths(obj):
        if isinstance(obj, dict):
            return {k: rewrite_paths(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [rewrite_paths(v) for v in obj]
        if isinstance(obj, str):
            return rewrite_str(obj)
        return obj

    def rewrite_str(s: str) -> str:
        s = re.sub(
            r"\$\{UMBREL_ROOT\}/data/storage/downloads/?",
            "${RUNTIPI_MEDIA_DIR}/downloads/",
            s,
        )
        s = re.sub(
            r"\$\{UMBREL_ROOT\}/data/storage/?",
            "${RUNTIPI_MEDIA_DIR}/",
            s,
        )
        s = re.sub(
            r"\$\{UMBREL_ROOT\}/data/storage/(.*)",
            r"${RUNTIPI_MEDIA_DIR}/\1",
            s,
        )
        s = re.sub(r"\$\{UMBREL_ROOT\}", "${RUNTIPI_MEDIA_DIR}", s)
        # umbrel's DEVICE_DOMAIN_NAME/hostname used inside URLs is the device's
        # public URL; map it to runtipi's APP_DOMAIN so apps generate redirects /
        # websocket origins / oidc callbacks against the real access URL instead
        # of the container-internal "localhost" (which crashes e.g. mailflow).
        s = re.sub(
            r"(?i)\bhttps?://\$\{DEVICE_DOMAIN_NAME\}(?::\d+)?",
            "${APP_PROTOCOL:-http}://${APP_DOMAIN}",
            s,
        )
        s = re.sub(
            r"(?i)\bhttps?://\$\{DEVICE_HOSTNAME\}(?::\d+)?",
            "${APP_PROTOCOL:-http}://${APP_DOMAIN}",
            s,
        )
        s = re.sub(r"\$\{DEVICE_DOMAIN_NAME\}|\$DEVICE_DOMAIN_NAME", "localhost", s)
        s = re.sub(r"\$\{DEVICE_HOSTNAME\}|\$DEVICE_HOSTNAME", "localhost", s)
        def _resolve_defaulted_var(m):
            return m.group(1) if m.group(1) else "localhost"
        s = re.sub(r"\$\{DEVICE_DOMAIN_NAME(?::-([^}]*))?\}", _resolve_defaulted_var, s)
        s = re.sub(r"\$\{DEVICE_HOSTNAME(?::-([^}]*))?\}", _resolve_defaulted_var, s)
        # umbrel-branded hardcoded defaults (device domain/email/credentials)
        s = s.replace("umbrel@umbrel.local", "admin@localhost")
        s = s.replace("admin@umbrel.local", "admin@localhost")
        s = s.replace("umbrel.local", "localhost")
        s = re.sub(r"(?<![\w.-])umbrelplane(?![\w.-])", "$APP_PASSWORD", s)
        if container_map:
            for cn, sname in container_map.items():
                s = re.sub(rf"(?<![\w.-]){re.escape(cn)}(?![\w.-])", sname, s)
        return s

    comp = rewrite_paths(comp)
    services = comp.setdefault("services", {})
    svc = services[main_service]

    # -- official-store conventions -----------------------------------------
    # runtipi marks its containers with the runtipi.managed label (used by the
    # "stop all"/"restart all" actions and container identification), and the
    # store standard is restart: unless-stopped rather than umbrel's on-failure.
    for sname, s in services.items():
        labels = s.get("labels")
        if isinstance(labels, dict):
            labels.setdefault("runtipi.managed", True)
        else:
            labels = [] if labels is None else labels
            if isinstance(labels, (list, tuple)):
                labels = list(labels)
            if not any("runtipi.managed" in str(l) for l in labels):
                labels.append("runtipi.managed=true")
            s["labels"] = labels
        if not isinstance(s.get("restart"), str) or s.get("restart") != "unless-stopped":
            s["restart"] = "unless-stopped"

    # -- x-runtipi metadata -------------------------------------------------
    svc.setdefault("x-runtipi", {})
    svc["x-runtipi"]["internal_port"] = internal_port
    svc["x-runtipi"]["is_main"] = True
    comp["x-runtipi"] = {"schema_version": 2}

    return comp, main_service, internal_port, host_port, notes


def build_form_fields(var_info: dict[str, bool]):
    """var_info: {VAR: has_default}. Only add fields for vars without default."""
    fields = []
    for var in sorted(var_info):
        if var in RUNTIPI_SYSTEM_VARS:
            continue
        if var_info[var]:
            continue  # has a default in compose, don't override
        if SECRET_RE.search(var):
            fields.append({
                "type": "random",
                "label": var.replace("APP_", "").replace("_", " ").title(),
                "env_variable": var,
                "required": False,
            })
        else:
            fields.append({
                "type": "text",
                "label": var.replace("APP_", "").replace("_", " ").title(),
                "env_variable": var,
                "required": False,
                "default": "",
            })
    return fields


def sanitize_text(s: str) -> str:
    """Remove umbrelOS/umbrel.local branding from user-facing text."""
    s = s.replace("umbrel@umbrel.local", "admin@localhost")
    s = s.replace("admin@umbrel.local", "admin@localhost")
    s = s.replace("umbrel.local", "localhost")
    s = s.replace("umbrelOS", "the server")
    s = re.sub(r"(?i)\bumbrel\b", "the server", s)
    return s


def build_config(manifest: dict, app_id: str, internal_port: int, var_info: dict[str, bool]) -> dict:
    name = manifest.get("name") or app_id
    category = manifest.get("category", "")
    categories = [CATEGORY_MAP.get(category, "utilities")]
    now = int(time.time() * 1000)

    form_fields = build_form_fields(var_info)

    cfg = {
        "$schema": "../app-info-schema.json",
        "name": name,
        "available": True,
        "exposable": True,
        "dynamic_config": True,
        "port": int(manifest["port"]) if manifest.get("port") else 0,
        "id": app_id,
        "tipi_version": 1,
        "version": str(manifest.get("version") or "latest"),
        "categories": categories,
        "description": sanitize_text((manifest.get("description") or "").strip()),
        "short_desc": sanitize_text((manifest.get("tagline") or "").strip()),
        "author": manifest.get("developer") or name,
        "source": manifest.get("repo") or manifest.get("website") or "",
        "website": manifest.get("website") or manifest.get("repo") or "",
        "form_fields": form_fields,
        "supported_architectures": ["arm64", "amd64"],
        "created_at": now,
        "updated_at": now,
        "min_tipi_version": "4.5.0",
    }
    return cfg


def description_md(manifest: dict) -> str:
    lines = ["# " + (manifest.get("name") or ""), ""]
    tagline = (manifest.get("tagline") or "").strip()
    if tagline:
        lines += [sanitize_text(tagline), ""]
    desc = (manifest.get("description") or "").strip()
    if desc:
        lines += [sanitize_text(desc), "", "---", ""]
    links = []
    if manifest.get("website"):
        links.append(f"- Website: {manifest['website']}")
    if manifest.get("repo"):
        links.append(f"- Repository: {manifest['repo']}")
    if manifest.get("support"):
        links.append(f"- Support: {manifest['support']}")
    if links:
        lines += ["## Links", ""] + links + [""]
    if manifest.get("defaultUsername") or manifest.get("defaultPassword"):
        lines += ["## Default credentials", ""]
        if manifest.get("defaultUsername"):
            lines.append(f"- Username: `{sanitize_text(str(manifest['defaultUsername']))}`")
        if manifest.get("defaultPassword"):
            lines.append(f"- Password: `{manifest['defaultPassword']}`")
        lines.append("")
    rn = (manifest.get("releaseNotes") or "").strip()
    if rn:
        lines += ["## Release notes", "", rn, ""]
    return "\n".join(lines)


def _render_svg_logo(svg_bytes: bytes, out_dir: Path, app_id: str) -> bool:
    """Render an SVG icon to metadata/logo.jpg (composited on white so
    transparent/black logos stay visible). Returns True on success."""
    from PIL import Image
    import subprocess
    svg_path = out_dir / "icon_tmp.svg"
    png_path = out_dir / "icon_tmp.png"
    try:
        svg_path.write_bytes(svg_bytes)
        subprocess.run(
            ["rsvg-convert", "-w", "256", "-h", "256", "-b", "white",
             "-o", str(png_path), str(svg_path)],
            check=True, capture_output=True,
        )
        img = Image.open(png_path).convert("RGB")
        # Reject renders that are essentially all one solid colour (no real
        # artwork) -- e.g. an icon whose content never reached the renderer.
        colors = img.getcolors(maxcolors=1000000) or [(1, (0, 0, 0))]
        if len(colors) < 3:
            raise ValueError(f"icon for {app_id} rendered as a solid block, skipping")
        img.save(str(out_dir / "logo.jpg"), "JPEG", quality=90)
        return True
    except Exception:
        return False
    finally:
        for p in (svg_path, png_path):
            p.unlink(missing_ok=True)


def download_logo(app_id: str, out_dir: Path) -> bool:
    # Repo logo fallbacks (real upstream logos): handle both raster (png/jpg)
    # and SVG sources -- rsvg-convert only understands SVG.
    if app_id in REPO_LOGO_FALLBACKS:
        url = REPO_LOGO_FALLBACKS[app_id]
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "runtipi-umbrel-converter"})
            raw = urllib.request.urlopen(req, timeout=30).read()
            lowered = url.lower()
            if lowered.endswith((".svg",)) or raw[:5].lstrip().startswith(b"<"):
                if _render_svg_logo(raw, out_dir, app_id):
                    return True
            else:
                from PIL import Image
                from io import BytesIO
                img = Image.open(BytesIO(raw)).convert("RGB")
                img.thumbnail((256, 256))
                img.save(str(out_dir / "logo.jpg"), "JPEG", quality=90)
                return True
        except Exception:
            pass
    # Umbrel gallery icon.svg (the default for converted apps).
    url = f"{ICON_BASE}/{app_id}/icon.svg"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "runtipi-umbrel-converter"})
        svg_data = urllib.request.urlopen(req, timeout=30).read()
    except Exception:
        return False
    return _render_svg_logo(svg_data, out_dir, app_id)


def placeholder_logo(out_dir: Path, label: str):
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (256, 256), (52, 65, 82))
        d = ImageDraw.Draw(img)
        d.rectangle([8, 8, 247, 247], outline=(120, 140, 160), width=4)
        d.text((128, 128), label[:1].upper(), fill=(255, 255, 255))
        img.save(str(out_dir / "logo.jpg"), "JPEG")
    except Exception:
        open(out_dir / "logo.jpg", "wb").write(b"")
        raise


# Images that are generic infrastructure ("main" service of both stores) and
# should NOT make two apps look like the same product. Everything else counts
# as an app-specific image.
INFRA_IMAGES = {
    name.lower()
    for name in (
        "postgres", "postgresql", "redis", "nginx", "mariadb", "mysql",
        "mongo", "memcached", "valkey", "clickhouse", "meilisearch",
        "getmeili/meilisearch", "onlyoffice/documentserver", "guacamole/guacd",
        "alpine", "bash", "busybox", "debian", "ubuntu", "traefik", "caddy",
        "zenika/alpine-chrome", "getumbrel/electrs", "getumbrel/docker-bitcoind",
        "postgres", "mariadb", "memcached", "valkey",
    )
}

# Hand-verified duplicates whose id/name differ between the Umbrel and Runtipi
# stores but which are the same product (confirmed by their images).
DEDUPE_ALIASES = {
    "adguard-home": "adguard",
    "changedetection-io": "changedetection",
    "firefly-iii-importer": "firefly-iii-data-importer",
    "kiwix": "kiwix-serve",
    "mosquitto": "eclipse-mosquitto",
    "mqttx-web": "mqttx",
    # umbrel's ollama is the generic/CPU build; amd/nvidia are distinct variants
    "ollama": "ollama-cpu",
    "plausible": "plausible-ce",
    "stalwart": "stalwart-mail",
    "trilium-notes": "trilium",
    "umami": "umami-analytics",
}


def image_repos(image_refs: list[str]) -> set[str]:
    """Normalise docker-compose image refs to {registry/org/repo} minus tag/digest."""
    repos = set()
    for img in image_refs or []:
        if not img:
            continue
        repo = img.split("@")[0].rsplit(":", 1)[0]
        repo = re.sub(
            r"^(docker\.io|ghcr\.io|quay\.io|gcr\.io|registry\.|index\.docker\.io)/",
            "", repo,
        )
        repos.add(repo)
    return repos


def app_specific_images(images: set[str]) -> set[str]:
    return {i for i in images if i.lower() not in INFRA_IMAGES}


def load_runtipi_catalog() -> dict:
    catalog = {}
    for cfg in (RUNTIPI_REPO / "apps").glob("*/config.json"):
        try:
            c = json.loads(cfg.read_text())
        except Exception:
            continue
        rid = c["id"].lower()
        images = set()
        try:
            comp = yaml.safe_load(
                (RUNTIPI_REPO / "apps" / c["id"] / "docker-compose.yml").read_text()
            ) or {}
            for svc in (comp.get("services") or {}).values():
                images |= image_repos([svc.get("image", "")])
        except Exception:
            pass
        catalog[rid] = {
            "name": c.get("name", c["id"]),
            "images": app_specific_images(images),
        }
    return catalog


def match_runtipi(umbrel_id: str, umbrel_name: str, umbrel_images: set[str], catalog: dict):
    ru_id = umbrel_id.lower()
    if ru_id in catalog:
        return ("id", ru_id)
    nid = norm(umbrel_id)
    for rid in catalog:
        if norm(rid) == nid:
            return ("normalized-id", rid)
    nname = norm(umbrel_name)
    for rid, rname in catalog.items():
        if norm(rname["name"]) == nname:
            return ("name", rid)
    if ru_id in DEDUPE_ALIASES and DEDUPE_ALIASES[ru_id] in catalog:
        return ("alias", DEDUPE_ALIASES[ru_id])
    # Image-based fallback: only match when the two apps share at least one
    # app-specific image AND one normalized name is contained in the other,
    # and exactly one runtipi app qualifies (avoids variant collisions like
    # ollama-cpu/amd/nvidia).
    my_images = app_specific_images(umbrel_images)
    if my_images:
        candidates = []
        for rid, info in catalog.items():
            if not (my_images & info["images"]):
                continue
            rname = norm(info["name"])
            if nname and rname and (nname in rname or rname in nname):
                candidates.append(rid)
        if len(candidates) == 1:
            return ("image", candidates[0])
    return None


def main():
    catalog = load_runtipi_catalog()
    app_dirs = sorted([d for d in UMBREL_REPO.iterdir() if d.is_dir() and (d / "umbrel-app.yml").exists()])

    skipped_dedup = []
    skipped_infra = []
    skipped_other = []
    converted = []
    failures = []
    used_ports = {}
    port_taken = set()

    # Pre-populate used ports from the Runtipi official store so host ports
    # don't clash with apps the user may already install from it.
    for cfg in (RUNTIPI_REPO / "apps").glob("*/config.json"):
        try:
            c = json.loads(cfg.read_text())
            if c.get("port"):
                port_taken.add(int(c["port"]))
                used_ports.setdefault(int(c["port"]), []).append("runtipi:" + c["id"])
        except Exception:
            pass

    # Never assign ports that are already in use on the user's server.
    for p in RESERVED_PORTS:
        port_taken.add(p)
        used_ports.setdefault(p, []).append("reserved (already in use)")

    for app_dir in app_dirs:
        app_id = app_dir.name
        try:
            manifest = yaml.safe_load((app_dir / "umbrel-app.yml").read_text()) or {}
            compose = yaml.load((app_dir / "docker-compose.yml").read_text(), Loader=ComposeLoader) or {}
        except Exception as e:
            failures.append((app_id, f"parse error: {e}"))
            continue

        # ---- deduce umbrel id/name (from manifest) ----------------------
        umbrel_id = manifest.get("id") or app_id
        umbrel_name = manifest.get("name") or app_id

        # ---- dedupe against runtipi --------------------------------------
        umbrel_images = set()
        for svc in (compose.get("services") or {}).values():
            umbrel_images |= image_repos([svc.get("image", "")])
        m = match_runtipi(umbrel_id, umbrel_name, umbrel_images, catalog)
        if m:
            skipped_dedup.append((app_id, m[1], m[0]))
            continue

        # ---- skip tor-only / no GUI --------------------------------------
        if manifest.get("torOnly"):
            skipped_other.append((app_id, "tor-only app"))
            continue
        if not umbrel_id:
            skipped_other.append((app_id, "missing id"))
            continue

        # ---- manual overrides (apps with a hook-free official image) ------
        # These apps are written by hand because their Umbrel package depends
        # on install hooks/templates, but an official upstream image works on
        # Runtipi via plain env vars. Skip all mechanical conversion for them.
        if app_id in MANUAL_COMPOSES:
            manual = MANUAL_COMPOSES[app_id]
            new_compose = manual["compose"]
            if manual.get("x-runtipi"):
                new_compose["x-runtipi"] = manual["x-runtipi"]
            cfg = build_config(manifest, app_id, 0, {})
            cfg["port"] = manual["port"]
            cfg["exposable"] = False
            cfg["form_fields"] = MANUAL_FORM_FIELDS.get(app_id, [])
            converted.append({
                "id": app_id,
                "name": cfg["name"],
                "compose": new_compose,
                "config": cfg,
                "manifest": manifest,
                "main_service": "otbr",
                "internal_port": manual["port"],
                "notes": [],
                "unnamed_vars": [],
            })
            continue

        # ---- skip apps that depend on Umbrel system infra -----------------
        compose_text = json.dumps(compose)
        all_vars = set(re.findall(r"\$\{?(APP_[A-Z0-9_]+)\}?", compose_text))
        infra_hits = sorted(
            v for v in all_vars
            if v.startswith(UMBREL_INFRA_PREFIXES) and v != "APP_DATA_DIR"
        )
        if "${UMBREL_ROOT}/app-data" in compose_text or "/app-data/lightning" in compose_text:
            infra_hits.append("UMBREL_ROOT/app-data")
        if infra_hits:
            skipped_infra.append((app_id, "umbrel system app dependency", ";".join(infra_hits[:6])))
            continue

        # ---- skip apps that depend on umbrel install hooks / templates -----
        # Apps whose containers mount or run files generated by umbrel
        # install/pre-start hooks (e.g. ${APP_DATA_DIR}/server.py from a
        # server.py.template) cannot run: runtipi has no hook mechanism, so the
        # mounted file never exists and the app crash-loops. Note: a plain
        # `env_file: settings.env` is NOT a skip reason -- convert already
        # strips env_file entries (see env_file removal in convert_compose).
        hook_deps = []
        if re.search(r"server\.py", compose_text) and (
            "server.py:" in compose_text or "server.py\"" in compose_text or "/app/server.py" in compose_text
        ):
            hook_deps.append("mounts/runs server.py (created by umbrel hook/template)")
        if hook_deps:
            skipped_other.append((app_id, "umbrel install hook/template dependency", ";".join(hook_deps)))
            continue

        # ---- convert -------------------------------------------------------
        try:
            new_compose, main_service, internal_port, host_port, notes = convert_compose(
                app_id, compose, int(manifest["port"]) if manifest.get("port") else 0
            )
        except Exception as e:
            failures.append((app_id, f"compose conversion failed: {e}"))
            continue

        apply_env_overrides(new_compose, app_id)

        var_info, all_vars = collect_vars(new_compose, app_id)

        cfg_port = host_port if host_port else (int(manifest["port"]) if manifest.get("port") else 0)
        if cfg_port == 0:
            failures.append((app_id, "missing port"))
            continue

        # assign a free host port if the umbrel port collides
        base = cfg_port
        while base in port_taken and base in used_ports:
            base = base + 1
        if base != cfg_port:
            notes.append(f"assigned new host port {base} (umbrel port {cfg_port} already used)")
        port_taken.add(base)
        used_ports.setdefault(base, []).append(app_id)

        cfg = build_config(manifest, app_id, internal_port, var_info)
        if app_id in MANUAL_FORM_FIELDS:
            cfg["form_fields"] = MANUAL_FORM_FIELDS[app_id]
        cfg["port"] = base

        if main_service:
            pass

        converted.append({
            "id": app_id,
            "name": cfg["name"],
            "compose": new_compose,
            "config": cfg,
            "manifest": manifest,
            "main_service": main_service,
            "internal_port": internal_port,
            "notes": notes,
            "unnamed_vars": sorted(v for v in var_info if not var_info[v] and v not in RUNTIPI_SYSTEM_VARS),
        })

    # ------------------------------------------------------------------
    # extra hand-added apps (not in Umbrel catalogue)
    # ------------------------------------------------------------------
    for extra_id, extra in EXTRA_APPS.items():
        manifest = extra["manifest"]
        new_compose = extra["compose"]
        if extra.get("x-runtipi"):
            new_compose["x-runtipi"] = extra["x-runtipi"]
        cfg = build_config(manifest, extra_id, 0, {})
        cfg["port"] = extra["port"]
        cfg["exposable"] = extra.get("exposable", False)
        cfg["form_fields"] = extra.get("form_fields", [])
        converted.append({
            "id": extra_id,
            "name": cfg["name"],
            "compose": new_compose,
            "config": cfg,
            "manifest": manifest,
            "main_service": extra.get("main_service", extra_id),
            "internal_port": extra["port"],
            "notes": [],
            "unnamed_vars": [],
        })

    # ------------------------------------------------------------------
    # write output
    # ------------------------------------------------------------------
    # Only regenerate the apps/ directory so store-level files the user adds
    # (README, scripts, .gitignore, ...) are preserved across runs.
    if (OUT_DIR / "apps").exists():
        shutil.rmtree(OUT_DIR / "apps")
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "apps").mkdir(parents=True)

    logo_fail = []
    for app in converted:
        a_dir = OUT_DIR / "apps" / app["id"]
        (a_dir / "metadata").mkdir(parents=True)
        (a_dir / "config.json").write_text(
            json.dumps(app["config"], indent=2) + "\n", encoding="utf-8"
        )
        # sensible dump for docker-compose.yml
        comp_dump = yaml.safe_dump(
            app["compose"],
            sort_keys=False,
            default_flow_style=False,
            width=10000,
            allow_unicode=True,
        )
        # prevent PyYAML emitting $VAR refs as weird YAML aliases
        (a_dir / "docker-compose.yml").write_text(comp_dump, encoding="utf-8")
        (a_dir / "metadata" / "description.md").write_text(
            description_md(app["manifest"]), encoding="utf-8"
        )
        ok = download_logo(app["id"], a_dir / "metadata")
        if not ok:
            try:
                placeholder_logo(a_dir / "metadata", app["name"])
                logo_fail.append((app["id"], "placeholder logo (no svg)"))
            except Exception as e:
                logo_fail.append((app["id"], f"no logo, placeholder failed: {e}"))

    # copy schema + validation tooling
    shutil.copy2(RUNTIPI_REPO / "apps" / "app-info-schema.json", OUT_DIR / "app-info-schema.json")

    # ---- report ----------------------------------------------------------
    lines = []
    lines.append("# Umbrel -> Runtipi conversion report\n")
    lines.append(
        f"- Umbrel apps: {len(app_dirs)}  \n"
        f"- Already in Runtipi official store (deduped): {len(skipped_dedup)}  \n"
        f"- Require Umbrel bitcoin/lightning infra (skipped): {len(skipped_infra)}  \n"
        f"- Skipped other: {len(skipped_other)}  \n"
        f"- Conversion failures: {len(failures)}  \n"
        f"- **Converted: {len(converted)}**  \n"
    )
    lines.append("\n## Converted apps\n")
    for app in sorted(converted, key=lambda a: a["id"]):
        n = app["notes"]
        field_keys = [f["env_variable"] for f in app["config"]["form_fields"] if f["type"] == "random"]
        note_str = "; ".join(n)
        lines.append(
            f"- **{app['name']}** (`{app['id']}`) port {app['config']['port']}, "
            f"main={app['main_service']}, internal={app['internal_port']}"
        )
        if note_str:
            lines.append(f"  - notes: {note_str}")
        if field_keys:
            lines.append(f"  - auto-generated secret env vars: {', '.join(field_keys)}")
    lines.append("\n## Deduplicated (already in Runtipi)\n")
    for folder, rid, how in sorted(skipped_dedup):
        lines.append(f"- `{folder}` matched runtipi `{rid}` ({how})")
    lines.append("\n## Skipped: require Umbrel bitcoin/lightning infra\n")
    for folder, reason, hits in sorted(skipped_infra):
        lines.append(f"- `{folder}` — {reason} [{hits}]")
    lines.append("\n## Skipped: other\n")
    for row in sorted(skipped_other):
        if len(row) == 3:
            folder, reason, hits = row
            lines.append(f"- `{folder}` — {reason} [{hits}]")
        else:
            folder, reason = row
            lines.append(f"- `{folder}` — {reason}")
    lines.append("\n## Conversion failures\n")
    for folder, reason in sorted(failures):
        lines.append(f"- `{folder}` — {reason}")
    lines.append("\n## Icons\n")
    if logo_fail:
        for folder, why in sorted(logo_fail):
            lines.append(f"- `{folder}` — {why}")
    else:
        lines.append("- All icons downloaded from the Umbrel gallery.")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Converted: {len(converted)}")
    print(f"Deduped: {len(skipped_dedup)}")
    print(f"Skipped infra: {len(skipped_infra)}")
    print(f"Skipped other: {len(skipped_other)}")
    print(f"Failures: {len(failures)}")
    print(f"Output: {OUT_DIR}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()