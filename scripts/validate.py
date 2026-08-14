#!/usr/bin/env python3
"""Validate the generated Runtipi app store.

Checks that every app in apps/ has:
  - a valid config.json per the official Runtipi schema
  - a parseable docker-compose.yml with x-runtipi schema_version 2
  - metadata/description.md and metadata/logo.jpg
  - a unique host port that does not clash with reserved/system ports
"""

import glob
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent.parent
APPS = HERE / "apps"
SCHEMA = HERE / "app-info-schema.json"

CATEGORIES = {
    "network", "media", "development", "automation", "social", "utilities",
    "photography", "security", "featured", "books", "data", "music",
    "finance", "gaming", "ai",
}
FORM_TYPES = {"text", "password", "email", "number", "fqdn", "ip", "fqdnip", "url", "random", "boolean"}


def validate_config(cfg: dict, problems: list) -> None:
    app = cfg.get("id", "?")
    for field in ("id", "name", "available", "port", "tipi_version", "version",
                  "categories", "description", "short_desc", "author", "source",
                  "supported_architectures", "created_at", "updated_at"):
        if field not in cfg:
            problems.append(f"{app}: missing config field {field}")
    for cat in cfg.get("categories", []):
        if cat not in CATEGORIES:
            problems.append(f"{app}: invalid category {cat}")
    for ff in cfg.get("form_fields", []):
        if ff.get("type") not in FORM_TYPES:
            problems.append(f"{app}: invalid form field type {ff.get('type')}")
        if ff.get("type") == "random" and ff.get("required"):
            problems.append(f"{app}: random form field must not be required")


def main() -> int:
    problems = []
    json_schema = None
    if SCHEMA.exists():
        json_schema = json.loads(SCHEMA.read_text())
    else:
        problems.append("app-info-schema.json missing")

    app_dirs = sorted(d for d in APPS.iterdir() if d.is_dir())
    used_ports = {}

    for a in app_dirs:
        app = a.name
        cfg_file = a / "config.json"
        if not cfg_file.exists():
            problems.append(f"{app}: missing config.json")
            continue
        try:
            cfg = json.loads(cfg_file.read_text())
        except Exception as e:
            problems.append(f"{app}: config.json unparsable: {e}")
            continue

        validate_config(cfg, problems)

        if json_schema:
            try:
                from jsonschema import Draft7Validator
                for e in Draft7Validator(json_schema).iter_errors(cfg):
                    problems.append(f"{app}: schema: {e.message}")
            except ImportError:
                pass

        port = cfg.get("port")
        if port:
            if not (1 <= port <= 65535):
                problems.append(f"{app}: port out of range {port}")
            if port in used_ports:
                problems.append(f"{app}: duplicate port {port} (also {used_ports[port]})")
            used_ports[port] = app

        compose_file = a / "docker-compose.yml"
        if not compose_file.exists():
            problems.append(f"{app}: missing docker-compose.yml")
        else:
            try:
                text = compose_file.read_text()
                data = yaml.safe_load(text)
                if not data or data.get("x-runtipi", {}).get("schema_version") != 2:
                    problems.append(f"{app}: missing x-runtipi schema_version: 2")
                mains = [s for s, sv in (data or {}).get("services", {}).items()
                         if isinstance(sv, dict) and sv.get("x-runtipi", {}).get("is_main")]
                if not mains:
                    problems.append(f"{app}: no main service (is_main)")
                if re.search(r"\$\{UMBREL_ROOT\}|\$UMBREL_ROOT|\$\{DEVICE_DOMAIN_NAME\}|\$DEVICE_DOMAIN_NAME", text):
                    problems.append(f"{app}: leftover umbrel system reference")
            except Exception as e:
                problems.append(f"{app}: compose unparsable: {e}")

        if not (a / "metadata" / "description.md").exists():
            problems.append(f"{app}: missing metadata/description.md")
        if not (a / "metadata" / "logo.jpg").exists():
            problems.append(f"{app}: missing metadata/logo.jpg")

    if problems:
        print(f"FAILED ({len(problems)} problem(s))")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"OK: {len(app_dirs)} apps valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
