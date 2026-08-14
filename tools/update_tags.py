#!/usr/bin/env python3
"""
Update all app images to their latest available tags.

For every service image in the generated store:
  1. strips the pinned @sha256:... digest
  2. uses the `latest` tag when the registry publishes one
  3. otherwise queries the registry API (Docker Hub / GHCR / Quay) for the
     newest version tag and uses that
  4. updates config.json `version` accordingly

Results are cached in update-tags-cache.json to avoid re-querying.

Usage: python3 update_tags.py
"""

from __future__ import annotations

import json
import re
import time
import urllib.request
import urllib.parse
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
APPS = HERE.parent / "apps"
CACHE_FILE = HERE / "update-tags-cache.json"
UA = {"User-Agent": "runtipi-umbrel-store/1.0"}

SEMVER = re.compile(r"^v?(\d+)(\.(\d+))?(\.(\d+))?([-+].*)?$")


def http_json(url: str, headers=None, retries: int = 3) -> dict | None:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={**UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status == 200:
                    return json.loads(r.read().decode())
                return None
        except Exception as e:
            if attempt == retries - 1:
                print(f"    ! http fail {url}: {e}")
                return None
            time.sleep(2 * (attempt + 1))


def ghcr_token(repo: str) -> str | None:
    d = http_json(f"https://ghcr.io/token?scope=repository:{repo}:pull")
    return d.get("token") if d else None


def sort_key(tag: str):
    m = SEMVER.match(tag)
    if not m:
        return (0, 0, 0, 0)
    return tuple(int(x) if x else 0 for x in (m.group(1), m.group(3) or 0, m.group(5) or 0))


def pick_best(tags: list[str], preferred=("stable", "main", "release")) -> str | None:
    if "latest" in tags:
        return "latest"
    # filter to plain semver tags, ignore arch-specific suffixes like x-amd64
    plain = [t for t in tags if SEMVER.match(t) and not re.search(r"(amd64|arm64|armv7|i386|ppc64le|s390x|riscv64)", t, re.I)]
    if plain:
        return sorted(plain, key=sort_key)[-1]
    for p in preferred:
        if p in tags:
            return p
    return None


def resolve_tag(image: str) -> tuple[str, str | None]:
    """Returns (new_image_ref, resolved_tag). image has NO tag/digest."""
    base = image.split(":")[0]
    low = base.lower()
    if low.startswith("ghcr.io/"):
        repo = base[len("ghcr.io/") :]
        token = ghcr_token(repo)
        if not token:
            return base + ":latest", "latest"
        d = http_json(f"https://ghcr.io/v2/{repo}/tags/list", headers={"Authorization": f"Bearer {token}"})
        if not d or "latest" in (d.get("tags") or []):
            return base + ":latest", "latest"
        best = pick_best(d.get("tags") or [])
        if best:
            return f"{base}:{best}", best
        return base + ":latest", "latest"
    if low.startswith("quay.io/"):
        repo = base[len("quay.io/") :]
        d = http_json(f"https://quay.io/api/v1/repository/{repo}/tag/?limit=100&onlyActiveTags=true")
        if d and d.get("tags"):
            tags = [t["name"] for t in d["tags"]]
            if "latest" in tags:
                return base + ":latest", "latest"
            best = pick_best(tags)
            if best:
                return f"{base}:{best}", best
        return base + ":latest", "latest"
    # Docker Hub (default registry) - docker.io or bare
    if low.startswith("docker.io/"):
        repo = base[len("docker.io/") :]
    else:
        repo = base
    if "/" not in repo:
        repo = "library/" + repo
    d = http_json(f"https://hub.docker.com/v2/repositories/{repo}/tags/latest")
    if d:
        return base + ":latest", "latest"
    d = http_json(f"https://hub.docker.com/v2/repositories/{repo}/tags?page_size=100")
    if d and d.get("results"):
        tags = [t["name"] for t in d["results"]]
        best = pick_best(tags)
        if best:
            return f"{base}:{best}", best
    return base + ":latest", "latest"


def normalize_image(ref: str) -> tuple[str, str | None]:
    """Split an image reference into (base_without_tag, tag)."""
    # strip digest
    ref = ref.split("@")[0]
    if ":" in ref.rsplit("/", 1)[-1]:
        base, tag = ref.rsplit(":", 1)
        return base, tag
    return ref, None


def main() -> None:
    cache = {}
    if CACHE_FILE.exists():
        cache = json.loads(CACHE_FILE.read_text())

    compose_files = sorted((APPS / d / "docker-compose.yml") for d in APPS.iterdir() if (APPS / d / "docker-compose.yml").exists())

    # collect unique images
    images = set()
    for f in compose_files:
        data = yaml.safe_load(f.read_text()) or {}
        for svc in (data.get("services") or {}).values():
            if svc.get("image"):
                images.add(svc["image"])
    print(f"unique images to resolve: {len(images)}")

    resolved: dict[str, str] = {}
    for i, image in enumerate(sorted(images)):
        if image in cache:
            resolved[image] = cache[image]
            continue
        base, tag = normalize_image(image)
        if tag is None or tag.lower() == "latest":
            resolved[image] = base + ":latest"
            cache[image] = resolved[image]
            continue
        print(f"  [{i+1}/{len(images)}] {image} -> ", end="", flush=True)
        new_ref, tag2 = resolve_tag(base)
        print(tag2 or "latest")
        resolved[image] = new_ref
        cache[image] = new_ref
        time.sleep(0.3)

    CACHE_FILE.write_text(json.dumps(cache, indent=2) + "\n", encoding="utf-8")

    # apply to compose files + config.json version
    updated_apps = []
    for f in compose_files:
        app = f.parent.name
        text = f.read_text()
        new_text = text
        data = yaml.safe_load(text) or {}
        versions = set()
        changed = False
        for svc in (data.get("services") or {}).values():
            img = svc.get("image")
            if not img or img not in resolved:
                continue
            new_img = resolved[img]
            if new_img != img:
                changed = True
            # replace image line robustly: match the exact quoted/unquoted image string
            new_text = new_text.replace(img, new_img)
            base, tag = normalize_image(new_img)
            if tag and tag.lower() != "latest":
                versions.add(tag.lstrip("v"))
            else:
                versions.add("latest")
        if changed:
            f.write_text(new_text, encoding="utf-8")
            if f.parent == APPS / app:
                cfg_file = APPS / app / "config.json"
                if cfg_file.exists():
                    cfg = json.loads(cfg_file.read_text())
                    cfg["version"] = sorted(versions)[0] if len(versions) == 1 else "latest"
                    cfg_file.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
            updated_apps.append(app)

    print(f"\nupdated {len(updated_apps)} apps")


if __name__ == "__main__":
    main()
