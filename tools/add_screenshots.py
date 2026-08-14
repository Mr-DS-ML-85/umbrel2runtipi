#!/usr/bin/env python3
"""
Add preview screenshots to each app's metadata/description.md from the Umbrel
gallery.

The Runtipi app-details "notes" view renders description.md. Official store
apps embed preview screenshots there; the Umbrel conversion does not carry any
images, so the notes tab is text-only.

Every Umbrel app manifest has a `gallery:` field listing screenshot filenames
(e.g. `- 1.jpg`). The actual image files are hosted on the Umbrel apps gallery:
    https://getumbrel.github.io/umbrel-apps-gallery/<app_id>/<n>.<ext>
This tool reads the gallery list straight from the cloned umbrel-apps repo and
injects a `## Preview` section with those images into metadata/description.md.

Apps with an empty gallery list are skipped and reported. Hand-added apps
(not in the Umbrel catalogue) get screenshots from EXTRA_SCREENSHOTS.

Usage: python3 add_screenshots.py
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
APPS = ROOT / "apps"
UMBREL_REPO = ROOT / "umbrel-apps"
GALLERY_BASE = "https://getumbrel.github.io/umbrel-apps-gallery"
UA = {"User-Agent": "runtipi-umbrel-store/1.0"}

# Hand-added apps that are not in the Umbrel catalogue (see EXTRA_APPS in
# convert.py) have no `gallery:` manifest. Point them at real preview images
# from their upstream sites so their notes tab shows a screenshot like the
# converted apps do.
EXTRA_SCREENSHOTS = {
    "dokploy": ["https://dokploy.com/banner.png"],
    "coolify": ["https://cdn.coollabs.io/og-images/coolify.png"],
    "pterodactyl": ["https://cdn.pterodactyl.io/site-assets/carousel/screenshot-1.png"],
}


def main() -> None:
    done = skipped = missing = 0
    for app_dir in sorted(APPS.iterdir()):
        if not app_dir.is_dir():
            continue
        app_id = app_dir.name
        desc_path = app_dir / "metadata" / "description.md"
        if not desc_path.exists():
            continue

        # hand-added apps: use their configured screenshot URLs directly
        if app_id in EXTRA_SCREENSHOTS:
            urls = EXTRA_SCREENSHOTS[app_id]
            first_url = urls[0]
            try:
                req = urllib.request.Request(first_url, headers=UA, method="HEAD")
                with urllib.request.urlopen(req, timeout=15) as r:
                    if r.status != 200:
                        missing += 1
                        continue
            except Exception:
                try:
                    req = urllib.request.Request(first_url, headers=UA)
                    with urllib.request.urlopen(req, timeout=15) as r:
                        if r.status != 200:
                            missing += 1
                            continue
                except Exception:
                    missing += 1
                    continue
            inject(desc_path, urls)
            done += 1
            continue

        src_manifest = UMBREL_REPO / app_id / "umbrel-app.yml"
        if not src_manifest.exists():
            skipped += 1
            continue
        try:
            manifest = yaml.safe_load(src_manifest.read_text()) or {}
        except Exception:
            skipped += 1
            continue

        gallery = [f.strip() for f in (manifest.get("gallery") or []) if str(f).strip()]
        if not gallery:
            skipped += 1
            continue

        # validate at least the first gallery image resolves, so we never embed
        # broken links for apps whose assets aren't published
        first_url = f"{GALLERY_BASE}/{app_id}/{gallery[0]}"
        try:
            req = urllib.request.Request(first_url, headers=UA, method="HEAD")
            with urllib.request.urlopen(req, timeout=15) as r:
                if r.status != 200:
                    missing += 1
                    continue
        except Exception:
            # fall back to GET (some CDNs reject HEAD)
            try:
                req = urllib.request.Request(first_url, headers=UA)
                with urllib.request.urlopen(req, timeout=15) as r:
                    if r.status != 200:
                        missing += 1
                        continue
            except Exception:
                missing += 1
                continue

        urls = [f"{GALLERY_BASE}/{app_id}/{f}" for f in gallery]
        inject(desc_path, urls)
        done += 1

    print(f"embedded screenshots: {done}")
    print(f"no gallery images: {skipped}")
    print(f"gallery unavailable: {missing}")


def inject(desc_path: Path, urls: list[str]) -> None:
    """Insert a `## Preview` section before the Links/credentials section."""
    text = desc_path.read_text(encoding="utf-8")
    if "## Preview" in text:
        return
    lines = ["## Preview", ""]
    for u in urls:
        lines.append(f"![Preview]({u})")
    block = "\n".join(lines) + "\n"
    idx = text.find("\n## Links")
    if idx == -1:
        idx = text.find("\n## Default credentials")
    if idx == -1:
        text = text.rstrip() + "\n\n" + block
    else:
        text = text[:idx] + "\n\n" + block + "\n" + text[idx + 1 :]
    desc_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()